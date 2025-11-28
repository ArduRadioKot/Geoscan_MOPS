import React from 'react'
import styled from 'styled-components'

const Loader = () => (
  <StyledWrapper aria-live="polite" aria-busy="true">
    <span className="loader" />
  </StyledWrapper>
)

const StyledWrapper = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;

  .loader {
    width: 48px;
    height: 48px;
    display: inline-block;
    position: relative;
  }

  .loader::after,
  .loader::before {
    content: '';
    box-sizing: border-box;
    width: 48px;
    height: 48px;
    border: 2px solid black;
    position: absolute;
    left: 0;
    top: 0;
    animation: rotation 2s ease-in-out infinite alternate;
  }

  .loader::after {
    border-color: #ff3d00;
    animation-direction: alternate-reverse;
  }

  @keyframes rotation {
    0% {
      transform: rotate(0deg);
    }

    100% {
      transform: rotate(360deg);
    }
  }
`

export default Loader

