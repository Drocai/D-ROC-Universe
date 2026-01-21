// GET /api/find?q=<query> - Search projects
import { universeIndex, getAllProjects } from './_data.js';

export default function handler(req, res) {
  const query = (req.query.q || '').toLowerCase();

  if (!query) {
    return res.status(400).json({ error: "Missing query parameter 'q'" });
  }

  // Check aliases first
  if (universeIndex.searchAliases[query]) {
    return res.status(200).json({
      type: "alias",
      query,
      match: universeIndex.searchAliases[query],
      github: `https://github.com/Drocai/D-ROC-Universe/tree/master/${universeIndex.searchAliases[query]}`
    });
  }

  // Search projects
  const projects = getAllProjects();
  const matches = projects.filter(p =>
    p.name.toLowerCase().includes(query) ||
    p.id.toLowerCase().includes(query) ||
    (p.tags && p.tags.some(t => t.toLowerCase().includes(query)))
  );

  res.status(200).json({
    query,
    count: matches.length,
    results: matches.map(m => ({
      id: m.id,
      name: m.name,
      world: m.world,
      tier: m.tier,
      status: m.status,
      tags: m.tags,
      context: m.context,
      github: `https://github.com/Drocai/D-ROC-Universe/tree/master/${m.path}`
    }))
  });
}
