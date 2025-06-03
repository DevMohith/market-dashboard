const { fetchStockData } = require('./data/fetchStockPrices');
const { computeCorrelation } = require('./correlation/computeCorrelations');

(async () => {
  const aapl = await fetchStockData("AAPL");
  const msft = await fetchStockData("MSFT");

  const a = aapl.map(d => parseFloat(d.close));
  const b = msft.map(d => parseFloat(d.close));

  const score = computeCorrelation(a, b);
  console.log("Correlation Score:", score);
})();
