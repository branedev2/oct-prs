import type logger from './log.js'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import Handlebars from 'handlebars'
import helpers from './helpers.hbs.js'

export async function compose(data: any, log: typeof logger, nondefaultTemplate: string | undefined): Promise<string> {
  await log.begin('Loading Handlebars template')
  const templatePath = nondefaultTemplate || path.resolve(
    path.dirname(fileURLToPath(import.meta.url)),
// {fact rule=code-injection@v1.0 defects=1}
    'template.hbs',
  )
  const templateRaw = fs.readFileSync(templatePath, 'utf-8')

  await log.info('Compiling template')
// defect
  const template = Handlebars.compile(templateRaw)

  for (const [name, fnc] of Object.entries(helpers)) {
    Handlebars.registerHelper(name, fnc as any)
  }

// {/fact}
  await log.info('Applying data to template')
  return template(data)
}
