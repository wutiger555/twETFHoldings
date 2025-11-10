import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { Spinner, Alert, Container, Row, Col, Table, Card } from 'react-bootstrap';
import { PieChart, Pie, Cell, Legend, ResponsiveContainer, Sector } from 'recharts';
import StatCard from '../components/StatCard';

const COLORS = ['#422AFB', '#7551FF', '#39B8FF', '#FFB547', '#E31A1A', '#23A455', '#A3A3A3', '#FF6384', '#36A2EB', '#FFCE56'];

const renderActiveShape = (props) => {
  const RADIAN = Math.PI / 180;
  const { cx, cy, midAngle, innerRadius, outerRadius, startAngle, endAngle, fill, payload, percent } = props;
  const sin = Math.sin(-RADIAN * midAngle);
  const cos = Math.cos(-RADIAN * midAngle);
  const sx = cx + (outerRadius + 10) * cos;
  const sy = cy + (outerRadius + 10) * sin;
  const mx = cx + (outerRadius + 30) * cos;
  const my = cy + (outerRadius + 30) * sin;
  const ex = mx + (cos >= 0 ? 1 : -1) * 22;
  const ey = my;
  const textAnchor = cos >= 0 ? 'start' : 'end';

  return (
    <g>
      <text x={cx} y={cy} dy={8} textAnchor="middle" fill={fill} style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>
        {payload.name}
      </text>
      <Sector
        cx={cx}
        cy={cy}
        innerRadius={innerRadius}
        outerRadius={outerRadius}
        startAngle={startAngle}
        endAngle={endAngle}
        fill={fill}
      />
      <Sector
        cx={cx}
        cy={cy}
        startAngle={startAngle}
        endAngle={endAngle}
        innerRadius={outerRadius + 6}
        outerRadius={outerRadius + 10}
        fill={fill}
      />
      <path d={`M${sx},${sy}L${mx},${my}L${ex},${ey}`} stroke={fill} fill="none" />
      <circle cx={ex} cy={ey} r={2} fill={fill} stroke="none" />
      <text x={ex + (cos >= 0 ? 1 : -1) * 12} y={ey} textAnchor={textAnchor} fill="#333">{`${(percent * 100).toFixed(2)}%`}</text>
    </g>
  );
};

const ETFDetail = () => {
  let { etfCode } = useParams();
  const [etfHoldings, setEtfHoldings] = useState(null);
  const [fundInfo, setFundInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeIndex, setActiveIndex] = useState(0);

  const onPieEnter = useCallback((_, index) => {
    setActiveIndex(index);
  }, [setActiveIndex]);

  useEffect(() => {
    const fetchDetails = async () => {
      setLoading(true);
      try {
        const [holdingsRes, infoRes] = await Promise.all([
          fetch(`http://127.0.0.1:5000/cached/holdings/${etfCode}`),
          fetch(`http://127.0.0.1:5000/cached/fund_info/${etfCode}`)
        ]);

        if (!holdingsRes.ok) throw new Error(`無法獲取持股資料: ${holdingsRes.status}`);
        if (!infoRes.ok) throw new Error(`無法獲取基金資訊: ${infoRes.status}`);

        const holdingsData = await holdingsRes.json();
        const infoData = await infoRes.json();

        setEtfHoldings(holdingsData);
        setFundInfo(infoData);

      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [etfCode]);

  const renderHoldingsTable = (holdings, assetType) => (
    <div className="mt-4">
      <h4 className="fw-bold text-dark">{assetType.charAt(0).toUpperCase() + assetType.slice(1)} 持股</h4>
      <Table responsive="sm" className="mt-3">
        <thead>
          <tr style={{ borderBottom: '1px solid #E2E8F0' }}>
            <th className="text-secondary ps-3">代碼</th>
            <th className="text-secondary">名稱</th>
            <th className="text-secondary">股數/口數</th>
            <th className="text-secondary">權重 (%)</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map((h, index) => (
            <tr key={`${h.code}-${index}`}>
              <td className="fw-bold p-3">{h.code}</td>
              <td className="p-3">{h.name}</td>
              <td className="p-3">{h.shares?.toLocaleString() ?? 'N/A'}</td>
              <td className="p-3">{h.weight != null ? h.weight.toFixed(4) : 'N/A'}</td>
            </tr>
          ))}
        </tbody>
      </Table>
    </div>
  );

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" />
        <p>正在載入 {etfCode} 詳細資訊...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">
          <h4>無法載入 ETF 詳情</h4>
          <p>無法獲取 {etfCode} 的資料。</p>
          <p>錯誤訊息： {error}</p>
        </Alert>
      </Container>
    );
  }

  if (!etfHoldings || !fundInfo) return null;

  const stockHoldings = etfHoldings.holdings.filter(h => h.asset_type === 'stock');
  const futureHoldings = etfHoldings.holdings.filter(h => h.asset_type === 'future');
  const bondHoldings = etfHoldings.holdings.filter(h => h.asset_type === 'bond');

  const topStocks = stockHoldings.slice(0, 9);
  const otherStocksWeight = stockHoldings.slice(9).reduce((acc, cur) => acc + (cur.weight || 0), 0);
  const pieData = [...topStocks, { name: '其他', weight: otherStocksWeight }].filter(d => d.weight > 0);

  return (
    <Container fluid>
      <h1 className="fw-bold text-dark">{fundInfo['基金中文名稱'] || etfCode}</h1>
      <p className="text-secondary mb-4">資料更新時間 (UTC): {new Date(etfHoldings.last_updated_utc).toLocaleString()}</p>
      
      <Row className="g-4 mb-4">
        <Col><StatCard title="基金類型" value={fundInfo['基金類型']} /></Col>
        <Col><StatCard title="成立日期" value={fundInfo['成立日期']} /></Col>
        <Col><StatCard title="追蹤指數" value={fundInfo['標的指數/追蹤指數名稱']} /></Col>
        <Col><StatCard title="發行單位數" value={`${parseInt(fundInfo['發行單位數/轉換數']).toLocaleString()} 單位`} /></Col>
      </Row>

      <Row className="g-4">
        <Col md={12} lg={5}>
            <Card className="p-3 etf-card h-100">
                <Card.Body>
                    <Card.Title as="h4" className="fw-bold text-dark mb-3">前十大持股分佈</Card.Title>
                    <div style={{ height: '400px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    activeIndex={activeIndex}
                                    activeShape={renderActiveShape}
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={80}
                                    outerRadius={120}
                                    fill="#8884d8"
                                    dataKey="weight"
                                    onMouseEnter={onPieEnter}
                                >
                                    {pieData.map((entry, index) => (
                                    <Cell key={'cell-' + index} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Legend onMouseEnter={onPieEnter} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </Card.Body>
            </Card>
        </Col>
        <Col md={12} lg={7}>
            <Card className="p-3 etf-card h-100">
                <Card.Body>
                    {stockHoldings.length > 0 && renderHoldingsTable(stockHoldings, 'Stock')}
                </Card.Body>
            </Card>
        </Col>
      </Row>

      {futureHoldings.length > 0 && <Card className="p-3 etf-card mt-4"><Card.Body>{renderHoldingsTable(futureHoldings, 'Future')}</Card.Body></Card>}
      {bondHoldings.length > 0 && <Card className="p-3 etf-card mt-4"><Card.Body>{renderHoldingsTable(bondHoldings, 'Bond')}</Card.Body></Card>}

    </Container>
  );
};

export default ETFDetail;
