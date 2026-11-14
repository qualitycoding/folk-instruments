// Spike S11: can a console program create and destroy a GenericAudioProcessorEditor on Linux, with and without a display?
#include <juce_audio_utils/juce_audio_utils.h>
#include <cstdio>
struct P : juce::AudioProcessor {
  P() : AudioProcessor(BusesProperties().withOutput("Out", juce::AudioChannelSet::stereo(), true)) { addParameter(new juce::AudioParameterFloat(juce::ParameterID{"level", 1}, "Level", 0.0f, 1.0f, 0.7f)); }
  const juce::String getName() const override { return "Probe"; }
  void prepareToPlay(double, int) override {} void releaseResources() override {}
  void processBlock(juce::AudioBuffer<float>& b, juce::MidiBuffer&) override { b.clear(); }
  juce::AudioProcessorEditor* createEditor() override { return new juce::GenericAudioProcessorEditor(*this); }
  bool hasEditor() const override { return true; } bool acceptsMidi() const override { return true; } bool producesMidi() const override { return false; }
  double getTailLengthSeconds() const override { return 0; } int getNumPrograms() override { return 1; } int getCurrentProgram() override { return 0; }
  void setCurrentProgram(int) override {} const juce::String getProgramName(int) override { return {}; } void changeProgramName(int, const juce::String&) override {}
  void getStateInformation(juce::MemoryBlock&) override {} void setStateInformation(const void*, int) override {}
};
int main() {
  juce::ScopedJuceInitialiser_GUI gui;
  P p; std::unique_ptr<juce::AudioProcessorEditor> ed(p.createEditorAndMakeActive());
  std::printf("editor %s width %d height %d\n", ed ? "created" : "null", ed ? ed->getWidth() : 0, ed ? ed->getHeight() : 0);
  ed.reset(); std::puts("editor destroyed"); return 0;
}
