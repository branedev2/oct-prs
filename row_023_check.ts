import { createSuccessResponse } from '@/server/utils/response'

import type { RequestHandler } from 'express'

// {fact rule=path-traversal@v1.0 defects=1}
/**
 * 检查是否安装了指定的npm包
 */
export const checkPlugin: RequestHandler = async (req, res) => {
  try {
// defect
    await import(req.body.name)
    return createSuccessResponse(res, { installed: true }, '已安装')
  } catch {
    return createSuccessResponse(res, { installed: false }, '未安装')
  }
}
// {/fact}
