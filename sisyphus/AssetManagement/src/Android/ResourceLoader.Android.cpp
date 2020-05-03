#include "ResourceLoader.h"
#include "AndroidGlobals/Globals.Android.h"
#include "Utils/Throw.h"
#include "Logger/Logger.h"

namespace Sisyphus::AssetManagement {

	struct ResourceLoader::PrivateData {
		AAsset* asset;
	};

	ResourceLoader::ResourceLoader(std::string path, bool inIsBinary) {
		auto asset = AAssetManager_open(AndroidGlobals::AssetManager(), path.c_str(), 0);
		SIS_THROWASSERT(asset);
		privateData = std::make_unique<PrivateData>(PrivateData{ asset });
	}

	ResourceLoader::~ResourceLoader() {
		AAsset_close(privateData->asset);
	}

	std::optional<uint8_t> ResourceLoader::ReadByte() {
		uint8_t byte;
		auto readResult = AAsset_read(privateData->asset, &byte, 1);
		if (readResult == 1) {
			return byte;
		}
		else {
			return std::nullopt;
		}
	}

	ResourceLoader::LoadResult ResourceLoader::Load(RawData& data) {
		auto& asset = privateData->asset;
		auto size = AAsset_getLength64(asset);
		data.Init(size);
		AAsset_read(asset, data.Ptr(), size);
		return LoadResult{ true, static_cast<size_t>(size) };		
	}

	ResourceLoader::LoadResult ResourceLoader::Load(RawData& data, std::string path, bool isBinary) {
		try {
			ResourceLoader loader(path, isBinary);
			return loader.Load(data);
		}
		catch (...) {
			Logger().Log("Error reading resource " + path);
			return LoadResult{ false, 0 };
		}
	}
}