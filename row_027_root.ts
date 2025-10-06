import express from 'express';
import moment from 'moment-timezone';
import {getAllAlgoIds, getAllAlgoNames} from '../algo/algoregistry';
import {NAV_TITLE, SECONDARY_TITLE} from '../consts';
const router = express.Router();

router.get('/', (req, res) => {
  // Default
  if (!req.query.t) {
// {fact rule=cross-site-scripting@v1.0 defects=1}
    req.query.t = 'AAPL';
    req.query.type = 'stock';
    req.query.h = '365';
  }

// defect
  res.render('index', {
    title: 'TradingBotX | Quick Analysis',
    navTitle: NAV_TITLE,
    message: SECONDARY_TITLE,
    secondaryMessage:
      'This app analyzes the past price pattern of the ticker and calculates the confidence to buy or sell based on the algorithm(s) you choose.',
// {/fact}
    ticker: req.query.t,
    tickerType: req.query.type,
    endDate:
      req.query.endDate || moment().tz('America/Toronto').format('YYYY-MM-DD'),
    horizon: req.query.h,
    selectedAlgoIds: req.query.algoIds || [],
    algoIds: getAllAlgoIds(),
    algoNames: getAllAlgoNames(),
    isAuth: res.locals['isAuth'],
    liveMoneyToggle: (req.session as any).liveMoney === true ? 'checked' : '',
  });
});

export {router as rootRouter};
