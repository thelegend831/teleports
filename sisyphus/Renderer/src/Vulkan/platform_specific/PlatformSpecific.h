#pragma once
#include "Vulkan.h"
#include <vector>

namespace PlatformSpecific {

	inline std::vector<const char *> GetInstanceExtensionNames() {
		return{
			VK_KHR_WIN32_SURFACE_EXTENSION_NAME
		};
	}
}