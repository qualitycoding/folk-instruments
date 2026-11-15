# Question tree (R1)

One branch: engineering (`software` is the only active profile), split by subject. Each leaf names what it informs. Leaves marked (answered) point to the claims that answer them; (open) leaves became risks.

## A. Free reeds
- A1 What equations describe a free reed well enough to synthesise from, and do they oscillate when integrated simply? → D-010, D-011; T-100 to T-105. (answered: C-001 to C-004, C-053)
- A2 Where does the spectrum come from, and how do pitch and level depend on pressure? → D-013, D-016; T-102 to T-104. (answered: C-002, C-003, C-055)
- A3 How does one reed model cover six octaves? → D-012; T-100, T-101. (answered: C-059, C-060, C-061, after C-053's failure)
- A4 What does it cost per reed, and what sample rate does it need? → D-011, D-014; T-013. (answered: C-054, C-060)
- A5 Which of the input file's reed statements can be traced? → none used. (answered: C-005 to C-010)

## B. Harmonica
- B1 Layout of the diatonic in every key → D-020; T-002. (answered: C-011)
- B2 Which bends and overbends exist, and how deep? → D-021; T-003, T-111. (answered below the bar: C-012, C-013; risk R-001)
- B3 How does a bend arise physically, and can the model produce it? → D-022, DR-04. (partly answered: C-013)
- B4 Chromatic harmonica: layout, valves, bends → D-023; T-112. (answered below the bar: C-014)
- B5 Playing pressures, vibrato, hand effects → D-024. (open: C-016; design values)

## C. Accordion and melodion
- C1 Registers and ranks → D-030; T-004, T-120. (answered below the bar: C-017)
- C2 Tremolo tuning → D-031; T-121. (answered: C-018)
- C3 Cassotto → D-032; T-122. (open: C-019; design values)
- C4 Bend → D-033; T-123. (answered below the bar: C-020)
- C5 What do real accordion notes measure? → T-200, D-050. (answered: C-021, C-055)
- C6 Melodion: construction, ranges, breath behaviour → D-040, D-041; T-131 to T-134. (answered below the bar: C-023 to C-025)

## D. Plucked strings
- D1 Partials of a stiff string → D-060; T-005, T-141. (answered: C-026)
- D2 String damping → D-061; T-005, T-145. (answered, one source: C-027)
- D3 Paired strings: beating and two-stage decay → D-062; T-006, T-143, T-144. (answered: C-028, C-029, C-031)
- D4 Pluck position and plectrum → D-063; T-142. (answered: C-030; the plectrum low-pass is an assumption)
- D5 Octave courses → D-062, D-073; T-147. (answered by inference: C-042)

## E. Instruments
- E1 Mandolin tuning, scales, strings → D-070, D-072; T-007, T-140. (answered: C-034, C-037, C-038)
- E2 Mandolin body modes by construction → D-071; T-146. (answered, one source each: C-035, C-036)
- E3 Bouzouki tunings, scales, strings → D-073; T-007, T-140. (answered: C-039, C-040, C-052)
- E4 Bouzouki body modes → D-071; T-146. (open: C-041; risk R-002)

## F. Engineering
- F1 Framework version and build recipe → D-080; S-002, S-310. (answered: C-043, C-057)
- F2 Licences → D-081. (answered: C-044)
- F3 Plugin validation → D-082; T-300. (answered: C-045)
- F4 CI pins and runner labels → D-083, D-084; S-003. (answered: C-046, C-047)
- F5 Python tooling → D-085. (answered: C-048, C-058)
- F6 Are the frozen tests satisfiable and do they measure what they say? → the freeze. (answered: C-056)

## G. References
- G1 Redistributable recordings per instrument → D-050, D-051; T-200, T-201; gates G-L1 to G-L5. (answered: C-021, C-049 to C-051; open for harmonica and melodion)

Pruned: reed materials and reed geometry tables (the model takes no geometry beyond D-010); the Helmholtz formula (bodies are preset data); reed counts and compass of a full accordion (D-002 limits scope to the treble ranks).
