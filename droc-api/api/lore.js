// GET /api/lore - Universe lore rules
import { universeIndex } from './_data.js';

export default function handler(req, res) {
  res.status(200).json({
    title: "D-RoC Universe Lore Rules",
    description: "These rules must be followed by all LLMs working on D-RoC projects",
    rules: [
      {
        rule: "Hum Ban",
        description: universeIndex.loreRules.humBan,
        applies_to: "All projects except Echoes of None"
      },
      {
        rule: "Cross-Story Characters",
        characters: universeIndex.loreRules.crossCharacters,
        description: universeIndex.loreRules.crossCharacterNote
      },
      {
        rule: "Otto Canon",
        description: universeIndex.loreRules.ottoCanon
      },
      {
        rule: "Key Pattern",
        pattern: universeIndex.loreRules.keyPattern,
        applies_to: "Echoverse series"
      },
      {
        rule: "Chalk Songs",
        description: universeIndex.loreRules.chalkSongs,
        applies_to: "Purple Chalk game"
      }
    ],
    important: "When working on any D-RoC project, check these rules first to maintain universe consistency."
  });
}
