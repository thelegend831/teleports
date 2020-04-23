#include "Pch_AssetManagement.h"
#include "AssetManager.h"
#include "Utils\Logger.h"
#include "Utils/Throw.h"
#include "Filesystem/Filesystem.h"
#include "AssetUnpacked.h"

namespace Sisyphus::AssetManagement {
	AssetManager::AssetManager(std::string inAssetDir, bool isReadOnly):
		mainAssetDir(inAssetDir)
	{
		InitAssets(isReadOnly);
	}
	void AssetManager::InitAssets(bool isReadOnly)
	{
		auto paths = FindAllAssetPaths(mainAssetDir);
		for (auto&& p : paths) {
			if (!isReadOnly) {
				AddAsset(std::make_unique<AssetUnpacked>(p));
			}
			else {
				SIS_THROWASSERT(false);
			}
		}
	}
	void AssetManager::AddAsset(std::unique_ptr<Asset> asset)
	{
		Logger().BeginSection("Asset detected");
		Logger().Log("Id: " + uuids::to_string(asset->Metadata().Id()));
		Logger().Log("Name: " + asset->Metadata().Name());
		Logger().EndSection();
		assets.insert({ asset->Metadata().Id(), std::move(asset) });
	}
	const Asset& AssetManager::GetAsset(uuids::uuid id) const
	{
		auto findResult = assets.find(id);
		if (findResult == assets.end()) {
			throw std::runtime_error("Cannot find asset with id " + uuids::to_string(id));
		}
		return *(*findResult).second;
	}
	int AssetManager::GetAssetCount() const
	{
		return static_cast<int>(assets.size());
	}
	std::vector<std::string> AssetManager::FindAllAssetPaths(std::string dir)
	{
		std::vector<std::string> result;
		for (auto&& p : Fs::RecursiveDirectoryIterator(dir)) {
			if (Fs::IsRegularFile(p) && p.Extension().String() != ".meta") {
				result.push_back(p.String());
			}
		}
		return result;
	}
}