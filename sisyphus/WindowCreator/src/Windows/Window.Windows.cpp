#include "Pch_WindowCreator.h"
#include "Window.Windows.h"
#include "Utils/Throw.h"

namespace Sisyphus::WindowCreator {
	struct WindowsWindow::PrivateData {
		HINSTANCE hInstance;
		HWND window;
	};

	WindowsWindow::WindowsWindow(CreateInfo ci) :
		data(std::make_unique<PrivateData>())
	{
		data->hInstance = GetModuleHandle(nullptr);

		WNDCLASSEX winClass;
		winClass.cbSize = sizeof(WNDCLASSEX);
		winClass.style = CS_HREDRAW | CS_VREDRAW;
		winClass.lpfnWndProc = DefWindowProc;
		winClass.cbClsExtra = 0;
		winClass.cbWndExtra = 0;
		winClass.hInstance = data->hInstance;
		winClass.hIcon = LoadIcon(nullptr, IDI_APPLICATION);
		winClass.hCursor = LoadCursor(nullptr, IDC_ARROW);
		winClass.hbrBackground = (HBRUSH)GetStockObject(WHITE_BRUSH);
		winClass.lpszMenuName = nullptr;
		winClass.lpszClassName = "Class Name";
		winClass.hIconSm = LoadIcon(nullptr, IDI_WINLOGO);

		if (!RegisterClassEx(&winClass)) {
			throw std::runtime_error("Failed to register a Windows class");
		}

		RECT windowRect = { 0, 0, static_cast<LONG>(ci.extent.width), static_cast<LONG>(ci.extent.height)};
		AdjustWindowRect(&windowRect, WS_OVERLAPPEDWINDOW, FALSE);
		data->window = CreateWindowEx(
			0,
			"Class Name",
			"Window Name",
			WS_OVERLAPPEDWINDOW | WS_VISIBLE,
			0, 0,
			windowRect.right - windowRect.left,
			windowRect.bottom - windowRect.top,
			nullptr,
			nullptr,
			data->hInstance,
			nullptr
		);

		if (!data->window) {
			throw std::runtime_error("Window creation failed!");
		}
	}

	WindowsWindow::~WindowsWindow()
	{
		DestroyWindow(data->window);
	}

	WindowExtent WindowsWindow::GetExtent() const
	{
		RECT rect;
		auto retVal = GetClientRect(data->window, &rect);
		SIS_THROWASSERT_MSG(retVal != 0, "");
		return { static_cast<uint32_t>(rect.right), static_cast<uint32_t>(rect.bottom) };
	}

	std::optional<WindowEvent> WindowsWindow::GetEvent()
	{
		MSG message;
		BOOL bRet = PeekMessage(&message, data->window, 0, 0, PM_REMOVE);
		if (bRet == 0) {
			return std::nullopt;
		}

		std::optional<WindowEvent> result = std::nullopt;

		// WM_CLOSE only singals a request to close the window, 
		// handle it differently when you want to introduce an "Are you sure?" message
		if (message.message == WM_DESTROY || message.message == WM_QUIT || message.message == WM_CLOSE) {
			result = WindowEvent{ WindowEvent::Type::Close };
		}

		TranslateMessage(&message);
		DispatchMessage(&message);

		return result;
	}

	vk::UniqueSurfaceKHR WindowsWindow::GetVulkanSurface(vk::Instance instance)
	{
		vk::Win32SurfaceCreateInfoKHR surfaceCreateInfo(
			{},
			data->hInstance,
			data->window
		);
		return instance.createWin32SurfaceKHRUnique(surfaceCreateInfo);
	}
}
