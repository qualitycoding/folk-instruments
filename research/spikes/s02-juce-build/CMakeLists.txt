cmake_minimum_required(VERSION 3.22)
project(SpikeJuce VERSION 0.1.0 LANGUAGES C CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(JUCE_SOURCE_DIR "" CACHE PATH "Path to a JUCE checkout at the pinned tag")
add_subdirectory(${JUCE_SOURCE_DIR} juce EXCLUDE_FROM_ALL)
juce_add_plugin(SpikePlugin
  COMPANY_NAME "QualityCoding"
  PLUGIN_MANUFACTURER_CODE Qlcd
  PLUGIN_CODE Spk1
  FORMATS VST3 Standalone
  PRODUCT_NAME "Spike Plugin"
  IS_SYNTH TRUE
  NEEDS_MIDI_INPUT TRUE
  NEEDS_MIDI_OUTPUT FALSE
  COPY_PLUGIN_AFTER_BUILD FALSE)
target_sources(SpikePlugin PRIVATE src/Plugin.cpp)
target_compile_definitions(SpikePlugin PUBLIC JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_VST3_CAN_REPLACE_VST2=0 JUCE_DISPLAY_SPLASH_SCREEN=0)
target_link_libraries(SpikePlugin PRIVATE juce::juce_audio_utils PUBLIC juce::juce_recommended_config_flags juce::juce_recommended_warning_flags)
