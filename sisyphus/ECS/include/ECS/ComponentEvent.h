#pragma once
#ifdef __cpp_concepts
#include <concepts>
#endif
#include "uuid.h"

namespace Sisyphus::ECS {
	
	namespace Events {
		class ComponentEventBase {};

		class Initialization : public ComponentEventBase {
		public:
			static uuids::uuid Id();
		};
	}

	// When adding a new event - update the following:
	//   - HandleEvent in IComponent (Component.h)
	//   - UpdateSubscriberLists<T> in Entity (Entity.h)
#ifdef __cpp_concepts
	template<typename T>
	concept ComponentEvent =
		std::derived_from<T, Events::ComponentEventBase> &&
		requires {
			{T::Id()}->std::same_as<uuids::uuid>;
		};
#endif
}