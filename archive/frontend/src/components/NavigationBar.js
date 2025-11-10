import React from 'react';
import { Navbar, Container } from 'react-bootstrap';

const NavigationBar = () => {
  return (
    <Navbar bg="transparent" variant="light" expand="lg" className="pt-4">
      <Container>
        <Navbar.Brand href="/" className="fw-bold text-dark fs-4">
          ETF 持股儀表板
        </Navbar.Brand>
      </Container>
    </Navbar>
  );
};

export default NavigationBar;