#include <juce_audio_utils/juce_audio_utils.h>
class P : public juce::AudioProcessor {
public:
  P() : AudioProcessor(BusesProperties().withOutput("Output", juce::AudioChannelSet::stereo(), true)),
        apvts(*this, nullptr, "state", { std::make_unique<juce::AudioParameterFloat>(juce::ParameterID{"gain", 1}, "Gain", 0.0f, 1.0f, 0.5f) }) {}
  const juce::String getName() const override { return "Spike"; }
  void prepareToPlay(double, int) override {}
  void releaseResources() override {}
  void processBlock(juce::AudioBuffer<float>& b, juce::MidiBuffer&) override { b.clear(); }
  juce::AudioProcessorEditor* createEditor() override { return new juce::GenericAudioProcessorEditor(*this); }
  bool hasEditor() const override { return true; }
  bool acceptsMidi() const override { return true; }
  bool producesMidi() const override { return false; }
  double getTailLengthSeconds() const override { return 0; }
  int getNumPrograms() override { return 1; }
  int getCurrentProgram() override { return 0; }
  void setCurrentProgram(int) override {}
  const juce::String getProgramName(int) override { return {}; }
  void changeProgramName(int, const juce::String&) override {}
  void getStateInformation(juce::MemoryBlock& d) override { if (auto x = apvts.copyState().createXml()) copyXmlToBinary(*x, d); }
  void setStateInformation(const void* d, int n) override { if (auto x = getXmlFromBinary(d, n)) apvts.replaceState(juce::ValueTree::fromXml(*x)); }
  juce::AudioProcessorValueTreeState apvts;
};
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter() { return new P(); }
