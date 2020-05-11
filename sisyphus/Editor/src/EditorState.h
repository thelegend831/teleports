#pragma once
#include <vector>
#include <optional>
#include "Filesystem/Path.h"

namespace Sisyphus::Editor {

	class EditorState {
	public:
		const std::vector<Fs::Path> LastOpenedProjects() const;

		void SaveToFile(const Fs::Path& path) const;
		void ReadFromFile(const Fs::Path& path);

		void OnProjectOpened(const Fs::Path& path);
	private:
		std::vector<Fs::Path> lastOpenedProjects;
	};

}