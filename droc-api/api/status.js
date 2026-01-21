// GET /api/status - Universe status overview
import { universeIndex, getAllProjects } from './_data.js';

export default function handler(req, res) {
  const projects = getAllProjects();
  const counts = { deployed: 0, ready: 0, active: 0, placeholder: 0, concept: 0 };

  projects.forEach(p => {
    if (counts[p.status] !== undefined) counts[p.status]++;
  });

  const status = {
    summary: {
      total: projects.length,
      deployed: counts.deployed,
      ready: counts.ready,
      active: counts.active
    },
    worlds: {
      "game-world": {
        live: Object.values(universeIndex.worlds["game-world"].tiers.live).map(g => ({ name: g.name, url: g.url })),
        ready: Object.values(universeIndex.worlds["game-world"].tiers.ready).map(g => g.name),
        development: Object.values(universeIndex.worlds["game-world"].tiers.development).map(g => g.name)
      },
      "story-world": Object.values(universeIndex.worlds["story-world"].projects).map(p => p.name),
      "music-world": Object.values(universeIndex.worlds["music-world"].albums).map(a => a.name),
      "business-world": Object.values(universeIndex.worlds["business-world"].projects).map(p => p.name)
    }
  };

  res.status(200).json(status);
}
