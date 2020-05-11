#pragma once
#include <unordered_map>
#include <optional>
#include "Project.h"
#include "EditorState.h"

namespace Sisyphus::Editor {

	class Editor {
	public:
		Editor();
		Editor(const Editor&) = delete;
		Editor(Editor&&) = delete;
		~Editor();
		void operator=(const Editor&) = delete;
		void operator=(Editor&&) = delete;

		void ReadState();
		void SaveState();

		void OpenProject(const Fs::Path& path);
		void CloseCurrentProject();

	private:
		std::optional<Project> currentProject;
		EditorState state;
	};
}