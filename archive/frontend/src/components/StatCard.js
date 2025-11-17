import React from 'react';
import { Card } from 'react-bootstrap';

const StatCard = ({ title, value }) => {
  return (
    <Card className="etf-card h-100">
      <Card.Body>
        <Card.Title as="h6" className="text-secondary">{title}</Card.Title>
        <p className="fs-5 fw-bold text-dark mb-0">{value}</p>
      </Card.Body>
    </Card>
  );
};

export default StatCard;
