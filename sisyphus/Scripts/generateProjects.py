import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import uuid
import json
import traceback

msbuildXmlNamespace = 'http://schemas.microsoft.com/developer/msbuild/2003'
ET.register_namespace('', msbuildXmlNamespace)

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")

class Platform:
    def __init__(self, 
                 name, 
                 configurations, 
                 architectures, 
                 staticLibExt, 
                 dynamicLibExt):
        self.name = name
        self.configurations = configurations
        self.architectures = architectures
        self.staticLibExt = staticLibExt
        self.dynamicLibExt = dynamicLibExt

platforms = [
    Platform(
        "Windows",
        ["Debug", "Release"],
        ["x64"],
        ".lib",
        ".dll"
    ),
    Platform(
        "Android",
        ["Debug", "Release"],
        ["ARM", "ARM64"],
        ".a",
        ".so"
    )
]

solutionDir = "../"

def readProjectGuid(path):
    if os.path.exists(path):
        try:
            with open(path) as file:
                root = ET.parse(file).getroot()
                guidElem = root.find(".//{" + msbuildXmlNamespace + "}ProjectGuid")
                print("guid of " + os.path.basename(path) + " is " + guidElem.text)
                return uuid.UUID(guidElem.text)
        except Exception as e:
            print("Failed to read guid from " + str(path) + ": " + str(e))
    
    return uuid.uuid4()

def readFilterGuids(path):
    result = {}
    try:
        with open(path) as file:
            root = ET.parse(file).getroot()
            for filterElem in root.iterfind(".//{" + msbuildXmlNamespace + "}Filter"):
                uuidElem = filterElem.find("{{{0}}}UniqueIdentifier".format(msbuildXmlNamespace))
                if uuidElem != None:
                    filterName = filterElem.get("Include")
                    result[filterName] = uuidElem.text
                    print("guid of {0} in {1} is {2}".format(filterName, os.path.basename(path), uuidElem.text))
    except:
        print("Failed to read guid from {0}: {1}".format(path, traceback.format_exc()))

    return result

class ProjectInfo:
    def __init__(self, projName):
        self.name = projName
        try:
            path = os.path.join(self.projDir(), "{0}.projectInfo.json".format(projName))
            with open(path) as jsonFile:
                jsonData = json.load(jsonFile)
                self.outputType = jsonData["outputType"]
                self.dependencies = jsonData["dependencies"]
                self.precompiledHeaders = jsonData["precompiledHeaders"]
                self.test = jsonData["test"]
        except:
            print("Failed to read project info from {0}: {1}".format(path, traceback.format_exc()))

    def projDir(self):
        return os.path.join(solutionDir, self.name)

class TargetInfo:
    def __init__(self, projGuid, filterGuids, isTest, cppPaths, cppDirs):
        self.projGuid = projGuid
        self.filterGuids = filterGuids
        self.isTest = isTest
        self.cppPaths = cppPaths
        self.cppDirs = cppDirs

def projectConfigurations(platform):
    root = ET.Element("ItemGroup")
    root.set("Label", "ProjectConfigurations")
    for config in platform.configurations:
        for arch in platform.architectures:
            projConfigElem = ET.SubElement(root, "ProjectConfiguration")
            projConfigElem.set("Include", config + "|" + arch)
            configElem = ET.SubElement(projConfigElem, "Configuration")
            configElem.text = config
            archElem = ET.SubElement(projConfigElem, "Platform")
            archElem.text = arch

    return root

def globals(platform, projectInfo, projGuid):
    root = ET.Element("PropertyGroup")
    root.set("Label", "Globals")

    guidElem = ET.SubElement(root, "ProjectGuid")
    guidElem.text = str(projGuid)

    rootNsElem = ET.SubElement(root, "RootNamespace")
    rootNsElem.text = projectInfo.name

    targetSystemElem = ET.SubElement(root, "TargetSystem")
    targetSystemElem.text = platform.name

    if platform.name == "Windows":
        wtpverElem = ET.SubElement(root, "WindowsTargetPlatformVersion")
        wtpverElem.text = "10.0"
    elif platform.name == "Android":
        keywordElem = ET.SubElement(root, "Keyword")
        keywordElem.text = "Android"
        appTypeElem = ET.SubElement(root, "ApplicationType")
        appTypeElem.text = "Android"
        appTypeRevElem = ET.SubElement(root, "ApplicationTypeRevision")
        appTypeRevElem.text = "3.0"

    return root

def configurations(platform, projectInfo, isTest):
    roots = []
    for config in platform.configurations:
        for arch in platform.architectures:
            root = ET.Element("PropertyGroup")
            root.set("Condition", "'$(Configuration)|$(Platform)'=='" + config + "|" + arch + "'")
            root.set("Label", "Configuration")
            configTypeElem = ET.SubElement(root, "ConfigurationType")
            configTypeElem.text = projectInfo.outputType if not isTest else "Application"
            useDebugElem = ET.SubElement(root, "UseDebugLibraries")
            useDebugElem.text = "true" if config == "Debug" else "false"
            toolsetElem = ET.SubElement(root, "PlatformToolset")
            toolsetElem.text = "v142" if platform.name == "Windows" else "Clang_5_0"
            if platform.name == "Windows":
                if config == "Release":
                    wpoElem = ET.SubElement(root, "WholeProgramOptimization")
                    wpoElem.text = "true"
                charsetElem = ET.SubElement(root, "CharacterSet")
                charsetElem.text = "MultiByte"
            roots.append(root)
    return roots

def propsImportGroup(projectInfo, isTest):
    root = ET.Element("ImportGroup")
    root.set("Label", "PropertySheets")

    userPropsElem = ET.SubElement(root, "Import")
    userPropsElem.set("Project", R"$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props")
    userPropsElem.set("Condition", R"exists('$(UserRootDir)\Microsoft.Cpp.$(Platform).user.props')")
    userPropsElem.set("Label", "LocalAppDataPlatform")

    dependencies = ["General"]
    if isTest:
        dependencies.append("catch2")
        dependencies.append(projectInfo.name)
    else:
        if projectInfo.precompiledHeaders:
            dependencies.append("PrecompiledHeaders")
        for dep in projectInfo.dependencies:
            dependencies.append(dep)

    for dep in dependencies:
        importElem = ET.SubElement(root, "Import")
        importElem.set("Project", "$(SolutionDir)props\\" + dep + ".props")

    return root

def getCppPathsAndDirs(projName, platform, isTest):
    sourceDirs = ["src", "include", "test"]
    resultFiles = []
    resultDirs = set()
    excludedPlatforms = platforms.copy()
    excludedPlatforms.remove(platform)
    for srcDir in sourceDirs:
        srcPath = os.path.join(solutionDir, projName, srcDir)
        for root, dirs, files in os.walk(srcPath):
            if not (srcDir == "test" and not isTest):
                resultDirs.add(os.path.relpath(root, solutionDir))
                for dir in dirs:
                    resultDirs.add(os.path.relpath(os.path.join(root, dir), solutionDir))
            if (srcDir == "test") == (isTest):
                for file in files:
                    exclude = False
                    for excludedPlatform in excludedPlatforms:
                        if file.find("." + excludedPlatform.name + ".") != -1:
                            exclude = True
                            break
                    if exclude:
                        continue
                    resultFiles.append(os.path.relpath(os.path.join(root, file), os.path.join(solutionDir)))

    return resultFiles, resultDirs

def getIncludeDirsIncludesAndCompiles(targetInfo, platform, projName):
    includeDirGroup = ET.Element("ItemDefinitionGroup")
    clCompileElem = ET.SubElement(includeDirGroup, "ClCompile")
    includeDirElem = ET.SubElement(clCompileElem, "AdditionalIncludeDirectories")
    includeDirStr = ""
    for dir in targetInfo.cppDirs:
        includeDirStr += "$(SolutionDir)%s;" % dir
    includeDirStr += "%(AdditionalIncludeDirectories)"
    includeDirElem.text = includeDirStr
    includeGroup = ET.Element("ItemGroup")
    compileGroup = ET.Element("ItemGroup")
    for path in targetInfo.cppPaths:
        stem, extension = os.path.splitext(os.path.basename(path))
        if extension in (".h", ".hpp"):
            includeElem = ET.SubElement(includeGroup, "ClInclude")
            includeElem.set("Include", "$(SolutionDir)" + str(path))
        elif extension in (".c", ".cpp"):
            compileElem = ET.SubElement(compileGroup, "ClCompile")
            compileElem.set("Include", "$(SolutionDir)" + str(path))
            if (stem == "Pch." + projName or stem == "Pch_" + projName) and platform.name == "Windows":
                pchElem = ET.SubElement(compileElem, "PrecompiledHeader")
                pchElem.text = "Create"

    return (includeDirGroup, includeGroup, compileGroup)

def generateFiltersString(existingFilterUuidDict, cppPaths, projName):
    root = ET.Element("Project")
    root.set("ToolsVersion", "4.0")
    root.set("xmlns", msbuildXmlNamespace)
    filterGroup = ET.SubElement(root, "ItemGroup")
    includeGroup = ET.SubElement(root, "ItemGroup")
    compileGroup = ET.SubElement(root, "ItemGroup")
    filterNames = set()
    for path in cppPaths:
        filterName = os.path.dirname(path)
        if "test" in filterName:
            a = 2
        filterName = filterName.replace(projName + "\\include\\" + projName, "Public Headers")
        filterName = filterName.replace(projName + "\\src", "Source Files")
        filterName = filterName.replace(projName + "\\test", "Test Files")

        # add filter if not exists
        if not filterName in filterNames:
            filterNames.add(filterName)
            filterElem = ET.SubElement(filterGroup, "Filter")
            filterElem.set("Include", filterName)
            uuidElem = ET.SubElement(filterElem, "UniqueIdentifier")
            existingUuid = existingFilterUuidDict.get(filterName) 
            if existingUuid != None:
                print("{1} - Existing filter uuid detected: {0}".format(existingUuid, filterName))
                uuidElem.text = str(existingUuid)
            else:
                newUuid = uuid.uuid4()
                print("{1} - Existing filter uuid not detected, generating: {0}".format(newUuid, filterName))
                uuidElem.text = str(newUuid)

        ext = os.path.splitext(path)[1]
        isHeader = ext in (".h", ".hpp")
        isCpp = ext in (".c", ".cpp")
        if isHeader:
            clElem = ET.SubElement(includeGroup, "ClInclude")
        elif isCpp:
            clElem = ET.SubElement(compileGroup, "ClCompile")
        else:
            print("{0} is neither a header nor a cpp file, no filter for it".format(path))
            continue
        clElem.set("Include", "$(SolutionDir){0}".format(path))
        filterElem = ET.SubElement(clElem, "Filter")
        filterElem.text = filterName

    return prettify(root)

def generateVcxprojString(platform, projectInfo, targetInfo):
    root = ET.Element("Project")
    root.set("DefaultTargets", "Build")
    root.set("xmlns", msbuildXmlNamespace)

    root.append(projectConfigurations(platform))
    root.append(globals(platform, projectInfo, targetInfo.projGuid))

    defaultPropsElem = ET.Element("Import")
    defaultPropsElem.set("Project", R"$(VCTargetsPath)\Microsoft.Cpp.Default.props")
    root.append(defaultPropsElem)

    for elem in configurations(platform, projectInfo, targetInfo.isTest):
        root.append(elem)

    cppPropsElem = ET.Element("Import")
    cppPropsElem.set("Project", R"$(VCTargetsPath)\Microsoft.Cpp.props")
    root.append(cppPropsElem)

    extSettingsElem = ET.Element("ImportGroup")
    extSettingsElem.set("Label", "ExtensionSettings")
    root.append(extSettingsElem)

    sharedElem = ET.Element("ImportGroup")
    sharedElem.set("Label", "Shared")
    root.append(sharedElem)
    
    root.append(propsImportGroup(projectInfo, targetInfo.isTest))

    userMacrosElem = ET.Element("PropertyGroup")
    userMacrosElem.set("Label", "UserMacros")

    includeDirGroup, includeGroup, compileGroup = getIncludeDirsIncludesAndCompiles(targetInfo, platform, projectInfo.name)
    root.append(includeDirGroup)
    root.append(includeGroup)
    root.append(compileGroup)

    targetsImportElem = ET.Element("Import")
    targetsImportElem.set("Project", R"$(VCTargetsPath)\Microsoft.Cpp.targets")
    root.append(targetsImportElem)

    extTargetsElem = ET.Element("ImportGroup")
    extTargetsElem.set("Label", "ExtensionTargets")
    root.append(extTargetsElem)

    return prettify(root)

def generateVcxprojAndFilters(platform, projectInfo, isTest):
    targetDir = os.path.join(projectInfo.projDir(), platform.name)
    if isTest:
        targetDir += ".Test"

    if not os.path.exists(targetDir):
        print("Creating target directory: " + targetDir)
        os.makedirs(targetDir)

    projFilename = projectInfo.name + "." + platform.name
    if isTest:
        projFilename += ".Test"
    projFilename += ".vcxproj"

    projPath = os.path.join(targetDir, projFilename)
    filtersPath = projPath + ".filters"
    cppPaths, cppDirs = getCppPathsAndDirs(projectInfo.name, platform, isTest)
    targetInfo = TargetInfo(
        projGuid = readProjectGuid(projPath), 
        filterGuids = readFilterGuids(filtersPath), 
        isTest = isTest,
        cppPaths = cppPaths,
        cppDirs = cppDirs)

    try:
        vcxprojString = generateVcxprojString(platform, projectInfo, targetInfo)
        with open(projPath, 'w') as projFile:
            projFile.write(vcxprojString)
            print(projFilename + " generated!")
    except:
        print("Failed to generate {0}: {1}".format(projFilename, traceback.format_exc()))

    try:
        filtersString = generateFiltersString(
            existingFilterUuidDict = targetInfo.filterGuids, 
            projName = projectInfo.name, 
            cppPaths = targetInfo.cppPaths)
        with open(filtersPath, 'w') as filtersFile:
            filtersFile.write(filtersString)
            print(os.path.basename(filtersPath) + " generated!")
    except:
        print("Failed to generate {0}: {1}".format(os.path.basename(filtersPath), traceback.format_exc()))

def generatePropsString(projectInfo):
    root = ET.Element("Project")
    root.set("xmlns", msbuildXmlNamespace)
    root.set("ToolsVersion", "4.0")

    importGroup = ET.SubElement(root, "ImportGroup")
    importGroup.set("Label", "PropertySheets")

    for dep in projectInfo.dependencies:
        importElem = ET.SubElement(importGroup, "Import")
        importElem.set("Condition", "'$(" + dep + "Imported)' == ''")
        importElem.set("Project", dep + ".props")

    propertyGroup = ET.SubElement(root, "PropertyGroup")
    imported = [*[projectInfo.name], *projectInfo.dependencies]
    for imp in imported:
        importedElem = ET.SubElement(propertyGroup, imp + "Imported")
        importedElem.text = "true"

    itemDefGroup = ET.SubElement(root, "ItemDefinitionGroup")
    clCompileElem = ET.SubElement(itemDefGroup, "ClCompile")
    includeDirElem = ET.SubElement(clCompileElem, "AdditionalIncludeDirectories")
    includeDirElem.text = "$SolutionDir" + projectInfo.name + "\include;%(AdditionalIncludeDirectories)"

    for platform in platforms:
        platformItemDefGroup = ET.SubElement(root, "ItemDefinitionGroup")
        platformItemDefGroup.set("Condition", "'$(TargetSystem)' == '" + platform.name + "'")
        linkElem = ET.SubElement(platformItemDefGroup, "Link")
        librarianElem = ET.SubElement(platformItemDefGroup, "Lib")
        libDirElem = ET.Element("AdditionalLibraryDirectories")
        libDirElem.text = "$(SolutionDir)%s\%s\$(GeneralOutDir);%%AdditionalLibraryDirectories" % (projectInfo.name, platform.name)
        libDependenciesElem = ET.Element("AdditionalDependencies")
        libDependenciesElem.text = "%s.%s%s;%%(AdditionalDependencies)" % (projectInfo.name, platform.name, platform.staticLibExt)
        linkElem.append(libDirElem)
        linkElem.append(libDependenciesElem)
        librarianElem.append(libDirElem)
        librarianElem.append(libDependenciesElem)

    return prettify(root)

def generateProps(projectInfo):
    propsPath = os.path.join(solutionDir, "props", "%s.props" % projectInfo.name)
    with open(propsPath, 'w') as propsFile:
        propsFile.write(generatePropsString(projectInfo))
        print(os.path.basename(propsPath) + " generated!")

def generateProject(projectInfo):
    for platform in platforms:
        generateVcxprojAndFilters(platform, projectInfo, False)
        if projectInfo.test:
            generateVcxprojAndFilters(platform, projectInfo, True)
    generateProps(projectInfo)


projects = ["AssetManagement", "Utils"]
for info in [ProjectInfo(projName) for projName in projects]:
    generateProject(info)
