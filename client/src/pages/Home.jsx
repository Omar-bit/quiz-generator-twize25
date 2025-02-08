import React from 'react';
import Nav from '../components/Nav';
import Services from '../components/Services';

import Contactus from '../components/Contactus';
import Footer from '../components/Footer';
import '../styles/quizStyle.css';
import '../styles/subjects.css';
function Home() {
  return (
    <>
      <Nav />
      <Services />
 
      <Contactus />
      <Footer />
    </>
  );
}

export default Home;
