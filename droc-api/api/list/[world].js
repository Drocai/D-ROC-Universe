// GET /api/list/<world> - List projects in a world
import { universeIndex } from '../_data.js';

export default function handler(req, res) {
  const { world } = req.query;

  const worldMap = {
    games: "game-world",
    stories: "story-world",
    music: "music-world",
    business: "business-world"
  };

  const worldKey = worldMap[world] || world;
  const worldData = universeIndex.worlds[worldKey];

  if (!worldData) {
    return res.status(404).json({
      error: `Unknown world: ${world}`,
      validWorlds: ["games", "stories", "music", "business"]
    });
  }

  const result = {
    world: worldKey,
    projects: []
  };

  if (worldData.tiers) {
    result.tiers = {};
    for (const [tier, items] of Object.entries(worldData.tiers)) {
      result.tiers[tier] = Object.entries(items).map(([id, item]) => ({
        id,
        name: item.name,
        status: item.status,
        tags: item.tags,
        url: item.url
      }));
    }
  }

  if (worldData.projects) {
    result.projects = Object.entries(worldData.projects).map(([id, item]) => ({
      id,
      name: item.name,
      type: item.type,
      status: item.status,
      tags: item.tags
    }));
  }

  if (worldData.albums) {
    result.albums = Object.entries(worldData.albums).map(([id, item]) => ({
      id,
      name: item.name,
      status: item.status
    }));
  }

  res.status(200).json(result);
}
