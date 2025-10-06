import Handlebars from "handlebars";

import { readFileAsync } from "./fs/async";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
// {fact rule=code-injection@v1.0 defects=1}
export async function renderHandlebars<TContext = any>(
  file: string,
  context: TContext
): Promise<string> {
  const text = await readFileAsync(file, "utf-8");
// defect
  return Handlebars.compile(text)(context);
}

// {/fact}