#include "Pch_VulkanRenderer.h"
#include "PhysicalDevice.h"
#include "Instance.h"
#include "ComponentManager.h"
#include "Utils/Logger.h"

namespace Sisyphus::Rendering::Vulkan {

	SIS_DEFINE_ID(ComponentID_PhysicalDevice, "8ffebfd2bd1b4ac6a35aa814d230e234");

	void PhysicalDevice::Initialize(const ComponentManager& componentManager)
	{
		auto physicalDevices = componentManager.GetComponent<Instance>().GetVulkanObject().enumeratePhysicalDevices();
		if (physicalDevices.empty()) {
			SIS_THROW("No physical devices supporting Vulkan");
		}

		physicalDevice = physicalDevices[0];
		Logger::Get().Log("Creating a Vulkan Device from " + std::string(physicalDevice.getProperties().deviceName));
		Inspect();
	}
	uuids::uuid PhysicalDevice::TypeId()
	{
		return ComponentID_PhysicalDevice;
	}
	std::string PhysicalDevice::ClassName()
	{
		return "PhysicalDevice";
	}
	ComponentReferences PhysicalDevice::Dependencies()
	{
		return { {Instance::TypeId()} };
	}
	vk::PhysicalDevice PhysicalDevice::GetVulkanObject() const
	{
		return physicalDevice;
	}
	void PhysicalDevice::Inspect() const
	{
		auto& logger = Logger::Get();
		auto queueFamilyProperties = physicalDevice.getQueueFamilyProperties();
		logger.BeginSection("Queue Families:");
		int index = 1;
		for (auto&& props : queueFamilyProperties) {
			auto flags = props.queueFlags;
			logger.Log("#" + std::to_string(index) + ": " + vk::to_string(flags) + " Count: " + std::to_string(props.queueCount));
			index++;
		}
		logger.EndSection();
	}
}