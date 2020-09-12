/*
Copyright 2020 kubeflow.org.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

package v1beta1

// TransformerSpec defines transformer service for pre/post processing
type TransformerSpec struct {
	// Pass through Pod fields or specify a custom container spec
	CustomTransformer `json:",inline,omitempty"`
	// Extensions available in all components
	ComponentExtensionSpec `json:",inline"`
}

// GetImplementations returns the implementations for the component
func (s *TransformerSpec) GetImplementations() []ComponentImplementation {
	implementations := NonNilComponents([]ComponentImplementation{})
	// This struct is not a pointer, so it will never be nil; include if containers are specified
	if len(s.CustomTransformer.Spec.Containers) != 0 {
		implementations = append(implementations, &s.CustomTransformer)
	}
	return implementations
}

// GetImplementation returns the implementation for the component
func (s *TransformerSpec) GetImplementation() ComponentImplementation {
	return s.GetImplementations()[0]
}

// GetExtensions returns the extensions for the component
func (s *TransformerSpec) GetExtensions() *ComponentExtensionSpec {
	return &s.ComponentExtensionSpec
}