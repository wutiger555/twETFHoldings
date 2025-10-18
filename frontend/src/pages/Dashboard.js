import React, { useState, useEffect } from 'react';
import { Card, Row, Col, Container, Spinner, Alert } from 'react-bootstrap';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [groupedEtfs, setGroupedEtfs] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAndGroupEtfs = async () => {
      try {
        const response = await fetch('http://127.0.0.1:5000/cached/etfs');
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        
        const groups = data.reduce((acc, etf) => {
          const firm = etf.firm_name || '未知發行商';
          if (!acc[firm]) {
            acc[firm] = [];
          }
          acc[firm].push(etf);
          return acc;
        }, {});

        setGroupedEtfs(groups);
      } catch (e) {
        setError(e.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAndGroupEtfs();
  }, []);

  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status" />
        <p className="mt-2">正在載入 ETF 列表...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">
          <h4>資料載入失敗</h4>
          <p>無法從後端 API 獲取資料。請確認後端伺服器已正常運行：</p>
          <code>flask --app app/main run</code>
          <hr />
          <p className="mb-0">錯誤詳情： {error}</p>
        </Alert>
      </Container>
    );
  }

  return (
    <Container fluid>
      <h1 className="text-dark fw-bold mb-4">儀表板總覽</h1>
      {Object.entries(groupedEtfs).map(([firmName, etfs]) => (
        <div key={firmName} className="mb-5">
          <h3 className="text-dark fw-bold mb-3">{firmName}</h3>
          <Row xs={1} md={2} lg={3} xl={4} className="g-4">
            {etfs.map((etf) => (
              <Col key={etf.code}>
                <Link to={`/etf/${etf.code}`} className="card-link">
                  <Card className="h-100 etf-card">
                    <Card.Body className="d-flex flex-column">
                      <Card.Title className="fw-bold text-dark">{etf.code}</Card.Title>
                      <Card.Subtitle className="mb-2 text-muted">{etf.name}</Card.Subtitle>
                      <Card.Text className="mt-auto text-end text-primary fw-bold">
                        <small>{etf.firm_name}</small>
                      </Card.Text>
                    </Card.Body>
                  </Card>
                </Link>
              </Col>
            ))}
          </Row>
        </div>
      ))}
    </Container>
  );
};

export default Dashboard;
