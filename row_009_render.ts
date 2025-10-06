import ejs from 'ejs';
import { readFileSync } from 'fs';
import { join } from 'path';
import type { NextApiRequest, NextApiResponse } from 'next'

const templateHash = {

}
// {fact rule=path-traversal@v1.0 defects=0}

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'POST') {
    try {
      const { template } = req.query
// defect
      const templat = readFileSync(join(process.cwd(), 'views', 'templateFour.ejs'), 'utf8');
      const html = ejs.render(templat, {
        data: req.body.data,
        colorList: req.body.colorList,
        page: 1
      });
// {/fact}
      // console.log(html)

      res.status(200).json({ html });
    } catch (error) {
      res.status(500).json({ error: 'Error rendering template' });
    }
  } else {
    res.status(405).json({ error: 'Method not allowed' });
  }
}