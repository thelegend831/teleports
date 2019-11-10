#include <exception>
#include <iostream>
#include "VulkanRenderer\Renderer.h"
#include "Utils\Logger.h"
#include "AssetManagement/AssetManager.h"

int main() {
	try {
		AssetManagement::AssetManager assetManager("Assets");

		auto logger = &Logger::Get();
		Vulkan::Renderer::CreateInfo rendererCreateInfo;
		rendererCreateInfo.windowWidth = 1280;
		rendererCreateInfo.windowHeight = 720;
		rendererCreateInfo.logger = logger;

		logger->BeginSection("Vulkan Renderer");
		Vulkan::Renderer renderer(rendererCreateInfo);

		// Shaders
		auto vertexShaderFileId = uuids::uuid::from_string("e1124008-e112-4008-a2f3-cf6233498020").value();
		String vertexShaderText(assetManager.GetAsset(vertexShaderFileId).GetDataAsString());
		auto fragmentShaderFileId = uuids::uuid::from_string("ce637e01-1d00-405c-8aaa-f0c022235745").value();
		String fragmentShaderText(assetManager.GetAsset(fragmentShaderFileId).GetDataAsString());

		auto vertexShaderId = renderer.CreateShader(
			vertexShaderText,
			ShaderType::Vertex);

		auto fragmentShaderId = renderer.CreateShader(
			fragmentShaderText,
			ShaderType::Fragment);

		renderer.EnableShader(vertexShaderId);
		renderer.EnableShader(fragmentShaderId);

		renderer.InitPipeline();
		logger->EndSection();

		// Uniform buffer
		Vulkan::Renderer::UniformBufferData ubData{ 255, 0, 0 };
		renderer.UpdateUniformBuffer(ubData);
		logger->Log("Uniform Buffer updated with 255, 0, 0!");

		auto ubDataFromGPU = renderer.GetUniformBufferData();
		if (memcmp(&ubData, &ubDataFromGPU, sizeof(ubData)) != 0) {
			throw std::logic_error("Uniform buffer data manipulation error!");
		}

		// Vertex buffer
		Vulkan::Renderer::VertexBufferData vbData{
			{
				{ 0.2f, 0.2f, 0.f },
				{ 0.2f, 0.8f, 0.f },
				{ 0.8f, 0.8f, 0.f },
				{ 0.8f, 0.2f, 0.f },
			}
		};
		renderer.UpdateVertexBuffer(vbData);
		logger->Log("Vertex Buffer updated!");

		auto vbDataFromGPU = renderer.GetVertexBufferData();
		if (memcmp(&vbData, &vbDataFromGPU, sizeof(vbData)) != 0) {
			throw std::logic_error("Vertex buffer data manipulation error!");
		}
	}
	catch (std::exception& e) {
		std::cout << e.what() << std::endl;
		system("PAUSE");
	}
}