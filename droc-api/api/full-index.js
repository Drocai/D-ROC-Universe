// GET /api/full-index - Full universe index
import { universeIndex } from './_data.js';

export default function handler(req, res) {
  res.status(200).json(universeIndex);
}
