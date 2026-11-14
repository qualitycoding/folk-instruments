# The five plugins. Each is the same wrapper (plugins/common) compiled for one instrument (plan/DECISIONS.md, D-094).
add_compile_definitions(JUCE_WEB_BROWSER=0 JUCE_USE_CURL=0 JUCE_VST3_CAN_REPLACE_VST2=0 JUCE_DISPLAY_SPLASH_SCREEN=0 JUCE_REPORT_APP_USAGE=0)

if(FOLK_JUCE_DIR)
  add_subdirectory(${FOLK_JUCE_DIR} ${CMAKE_BINARY_DIR}/juce EXCLUDE_FROM_ALL)
else()
  FetchContent_Declare(JUCE GIT_REPOSITORY https://github.com/juce-framework/JUCE.git GIT_TAG ${FOLK_JUCE_COMMIT})
  FetchContent_MakeAvailable(JUCE)
endif()

function(folk_add_plugin target product code instrument)
  juce_add_plugin(${target}
    COMPANY_NAME "QualityCoding"
    BUNDLE_ID "org.qualitycoding.${target}"
    PLUGIN_MANUFACTURER_CODE Qlcd
    PLUGIN_CODE ${code}
    FORMATS VST3 Standalone
    PRODUCT_NAME "${product}"
    IS_SYNTH TRUE
    NEEDS_MIDI_INPUT TRUE
    NEEDS_MIDI_OUTPUT FALSE
    IS_MIDI_EFFECT FALSE
    VST3_CATEGORIES Instrument Synth
    COPY_PLUGIN_AFTER_BUILD FALSE)
  target_sources(${target} PRIVATE common/FolkProcessor.cpp)
  target_compile_definitions(${target} PUBLIC FOLK_INSTRUMENT=folk::Instrument::${instrument})
  target_link_libraries(${target} PRIVATE folkdsp juce::juce_audio_utils PUBLIC juce::juce_recommended_config_flags)
  if(FOLK_BUILD_TESTS)
    # The host test compiles the wrapper source itself (it does not link the plugin target), so it sees JUCE's headers
    # and flags through its own module link.
    juce_add_console_app(${target}HostTest PRODUCT_NAME "${target}HostTest")
    target_sources(${target}HostTest PRIVATE ${CMAKE_SOURCE_DIR}/tests/juce/host_test.cpp common/FolkProcessor.cpp)
    target_compile_definitions(${target}HostTest PRIVATE FOLK_INSTRUMENT=folk::Instrument::${instrument})
    target_link_libraries(${target}HostTest PRIVATE folkdsp juce::juce_audio_utils Catch2::Catch2 PUBLIC juce::juce_recommended_config_flags)
    add_test(NAME ${target}HostTest COMMAND ${target}HostTest)
  endif()
endfunction()

folk_add_plugin(FolkHarmonica "Folk Harmonica" Fhrm Harmonica)
folk_add_plugin(FolkAccordion "Folk Accordion" Facc Accordion)
folk_add_plugin(FolkMelodion  "Folk Melodion"  Fmel Melodion)
folk_add_plugin(FolkMandolin  "Folk Mandolin"  Fman Mandolin)
folk_add_plugin(FolkBouzouki  "Folk Bouzouki"  Fbzk Bouzouki)
