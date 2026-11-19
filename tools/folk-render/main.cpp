// folk-render: renders an event file to a WAV file with the DSP core, without JUCE (plan/DECISIONS.md, D-092).
#include <algorithm>
#include <cerrno>
#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <fstream>
#include <locale>
#include <sstream>
#include <string>
#include <vector>
#include "folk/engine.h"

#ifndef FOLK_VERSION
#define FOLK_VERSION "0.1.0"
#endif

namespace {
enum Status { kOk = 0, kUsage = 2, kMalformed = 3, kFile = 4 };

struct Usage { std::string msg; };
struct Malformed { std::string msg; };

struct Ev { double t; char kind; int a; double v; std::string id; };

const char* kHelp =
    "usage: folk-render --instrument <harmonica|accordion|melodion|mandolin|bouzouki> --events <file> --out <file.wav>\n"
    "                   [--sr <44100..96000, default 48000>] [--block <1..8192, default 256>] [--set <id>=<value>]...\n"
    "       folk-render --instrument <name> --list-params\n"
    "       folk-render --instrument <name> --dump-model [--set <id>=<value>]...\n"
    "       folk-render --version | --help\n";

bool parseNumber(const std::string& s, double& out) {
    if (s.empty()) return false;
    std::istringstream is(s);
    is.imbue(std::locale::classic());
    is >> out;
    return !is.fail() && is.eof() && std::isfinite(out);
}

std::string fmt(double v) {
    std::ostringstream os;
    os.imbue(std::locale::classic());
    os << v;
    return os.str();
}

std::vector<Ev> parseEvents(const std::string& path, folk::Engine& e) {
    std::ifstream in(path, std::ios::binary);
    if (!in) throw std::runtime_error("cannot read event file " + path);
    std::vector<Ev> evs;
    std::string line;
    int lineNo = 0;
    double last = 0;
    bool ended = false;
    auto bad = [&](const std::string& why) { return Malformed{"line " + std::to_string(lineNo) + ": " + why}; };
    while (std::getline(in, line)) {
        ++lineNo;
        if (line.size() > 1000) throw bad("line longer than 1000 characters");
        if (!line.empty() && line.back() == '\r') line.pop_back();
        for (unsigned char c : line)
            if (c == 0 || (c < 32 && c != '\t') || c >= 0x80) { if (c == 0 || c < 32) throw bad("control character"); }
        std::istringstream is(line);
        std::string tok;
        if (!(is >> tok) || tok[0] == '#') continue;
        if (ended) throw bad("event after end");
        Ev ev{};
        if (!parseNumber(tok, ev.t) || ev.t < 0) throw bad("bad time");
        if (ev.t < last) throw bad("time decreases");
        if (ev.t > 600) throw bad("time above 600 s");
        last = ev.t;
        std::string kind, a, b, extra;
        if (!(is >> kind)) throw bad("missing event kind");
        double x = 0, y = 0;
        auto num = [&](std::string& s, double& d) { if (!(is >> s) || !parseNumber(s, d)) throw bad("bad number for " + kind); };
        if (kind == "on") { ev.kind = 'n'; num(a, x); num(b, y); ev.a = int(x); ev.v = y; }
        else if (kind == "off") { ev.kind = 'f'; num(a, x); ev.a = int(x); }
        else if (kind == "cc") { ev.kind = 'c'; num(a, x); num(b, y); ev.a = int(x); ev.v = y; }
        else if (kind == "bend") { ev.kind = 'b'; num(a, y); ev.v = y; }
        else if (kind == "set") {
            ev.kind = 's';
            if (!(is >> ev.id)) throw bad("missing parameter id");
            if (e.paramIndex(ev.id) < 0) throw bad("unknown parameter " + ev.id);
            num(b, y); ev.v = y;
        }
        else if (kind == "tap") { ev.kind = 't'; num(b, y); ev.v = y; }
        else if (kind == "end") { ev.kind = 'e'; ended = true; }
        else throw bad("unknown event kind '" + kind + "'");
        if (is >> extra) throw bad("unexpected extra text");
        evs.push_back(ev);
    }
    if (!ended) throw Malformed{"the end event is missing"};
    return evs;
}

void put32(std::vector<unsigned char>& b, uint32_t v) { for (int i = 0; i < 4; ++i) b.push_back((unsigned char)(v >> (8 * i))); }
void put16(std::vector<unsigned char>& b, uint16_t v) { b.push_back((unsigned char)v); b.push_back((unsigned char)(v >> 8)); }

bool writeWav(const std::string& path, const std::vector<float>& l, const std::vector<float>& r, int sr) {
    const uint32_t dataBytes = uint32_t(l.size() * 8);
    std::vector<unsigned char> h;
    h.insert(h.end(), {'R', 'I', 'F', 'F'}); put32(h, 36 + dataBytes);
    h.insert(h.end(), {'W', 'A', 'V', 'E', 'f', 'm', 't', ' '}); put32(h, 16);
    put16(h, 3); put16(h, 2); put32(h, uint32_t(sr)); put32(h, uint32_t(sr) * 8); put16(h, 8); put16(h, 32);
    h.insert(h.end(), {'d', 'a', 't', 'a'}); put32(h, dataBytes);
    const std::string tmp = path + ".tmp";
    {
        std::ofstream out(tmp, std::ios::binary | std::ios::trunc);
        if (!out) return false;
        out.write(reinterpret_cast<const char*>(h.data()), std::streamsize(h.size()));
        std::vector<unsigned char> buf;
        for (size_t i = 0; i < l.size(); ++i) {
            for (float s : {l[i], r[i]}) {
                uint32_t u;
                std::memcpy(&u, &s, 4);
                put32(buf, u);
            }
            if (buf.size() >= 65536 || i + 1 == l.size()) {
                out.write(reinterpret_cast<const char*>(buf.data()), std::streamsize(buf.size()));
                buf.clear();
            }
        }
        out.flush();
        if (!out) { out.close(); std::remove(tmp.c_str()); return false; }
    }
    if (std::rename(tmp.c_str(), path.c_str()) != 0) { std::remove(tmp.c_str()); return false; }
    return true;
}
}  // namespace

int main(int argc, char** argv) {
    std::string instName, eventsPath, outPath;
    std::vector<std::pair<std::string, std::string>> sets;
    double sr = 48000;
    int block = 256;
    bool listParams = false, dumpModel = false, version = false, help = false;
    try {
        for (int i = 1; i < argc; ++i) {
            const std::string a = argv[i];
            auto value = [&]() -> std::string {
                if (i + 1 >= argc) throw Usage{"missing value for " + a};
                return argv[++i];
            };
            if (a == "--instrument") instName = value();
            else if (a == "--events") eventsPath = value();
            else if (a == "--out") outPath = value();
            else if (a == "--sr") { if (!parseNumber(value(), sr)) throw Usage{"bad sample rate"}; }
            else if (a == "--block") { double b; if (!parseNumber(value(), b) || b != std::floor(b)) throw Usage{"bad block size"}; block = int(std::max(-1.0, std::min(b, 1e9))); }
            else if (a == "--set") {
                const std::string kv = value();
                const size_t eq = kv.find('=');
                if (eq == std::string::npos) throw Usage{"--set needs <id>=<value>"};
                sets.emplace_back(kv.substr(0, eq), kv.substr(eq + 1));
            }
            else if (a == "--list-params") listParams = true;
            else if (a == "--dump-model") dumpModel = true;
            else if (a == "--version") version = true;
            else if (a == "--help") help = true;
            else throw Usage{"unknown option " + a};
        }
        if (help) { std::fputs(kHelp, stdout); return kOk; }
        if (version) { std::printf("folk-render %s\n", FOLK_VERSION); return kOk; }
        folk::Instrument ins;
        if (!folk::instrumentFromName(instName, ins)) throw Usage{"unknown instrument '" + instName + "'"};
        if (sr < 44100 || sr > 96000 || sr != std::floor(sr)) throw Usage{"sample rate must be an integer from 44100 to 96000"};
        if (block < 1 || block > 8192) throw Usage{"block size must be 1 to 8192"};
        auto engine = folk::Engine::create(ins);
        if (listParams) {
            for (int i = 0; i < engine->numParams(); ++i) {
                const folk::ParamInfo p = engine->paramInfo(i);
                std::printf("%s\t%s\t%s\t%s\t%d\n", p.id, fmt(p.min).c_str(), fmt(p.max).c_str(), fmt(p.def).c_str(), p.steps);
            }
            return kOk;
        }
        for (const auto& kv : sets) {
            double d;
            const int idx = engine->paramIndex(kv.first);
            if (idx < 0) throw Usage{"unknown parameter '" + kv.first + "'"};
            if (!parseNumber(kv.second, d)) throw Usage{"bad value for parameter " + kv.first};
            engine->setParam(idx, float(d));
        }
        if (dumpModel) {
            std::printf("{\"instrument\": \"%s\"}\n", instName.c_str());
            return kOk;
        }
        if (eventsPath.empty() || outPath.empty()) throw Usage{"--events and --out are required"};
        std::vector<Ev> evs;
        try {
            evs = parseEvents(eventsPath, *engine);
        } catch (const std::runtime_error& e) {
            std::fprintf(stderr, "folk-render: %s\n", e.what());
            return kFile;
        }
        engine->prepare(sr, block);
        const long total = std::lround(evs.back().t * sr);
        std::vector<float> L(static_cast<size_t>(total)), R(static_cast<size_t>(total));
        std::vector<long> at(evs.size());
        for (size_t i = 0; i < evs.size(); ++i) at[i] = std::lround(evs[i].t * sr);
        long pos = 0;
        size_t next = 0;
        while (pos < total) {
            // 'set' events change a parameter at an exact sample, so the block is cut there; the others carry an offset.
            long end = std::min<long>(total, pos + block);
            for (size_t k = next; k < evs.size() && at[k] < end; ++k) {
                if (evs[k].kind == 's' && at[k] > pos) { end = at[k]; break; }
            }
            while (next < evs.size() && at[next] < end) {
                const Ev& e = evs[next];
                const int off = int(at[next] - pos);
                switch (e.kind) {
                    case 'n': engine->noteOn(e.a, float(e.v), off); break;
                    case 'f': engine->noteOff(e.a, off); break;
                    case 'c': engine->controlChange(e.a, float(e.v), off); break;
                    case 'b': engine->pitchBend(float(e.v), off); break;
                    case 's': engine->setParam(engine->paramIndex(e.id), float(e.v)); break;
                    default: break;  // tap: wired in S-240; end
                }
                ++next;
            }
            engine->process(L.data() + pos, R.data() + pos, int(end - pos));
            pos = end;
        }
        if (!writeWav(outPath, L, R, int(sr))) {
            std::fprintf(stderr, "folk-render: cannot write %s\n", outPath.c_str());
            return kFile;
        }
        return kOk;
    } catch (const Usage& u) {
        std::fprintf(stderr, "folk-render: %s\n%s", u.msg.c_str(), kHelp);
        return kUsage;
    } catch (const Malformed& m) {
        std::fprintf(stderr, "folk-render: %s\n", m.msg.c_str());
        return kMalformed;
    }
}
