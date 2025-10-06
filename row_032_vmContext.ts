// {fact rule=code-injection@v1.0 defects=1}
import vm, { Context } from "vm";

export const runInContext = (code: string, context: Context) => {
// defect
  vm.runInNewContext(code, context);
  return context;
};

// {/fact}