import { render, screen } from '@testing-library/react';
import App from './App';

test('renders stock analysis heading', () => {
  render(<App />);
  const headingElement = screen.getByText(/Stock Analysis/i);
  expect(headingElement).toBeInTheDocument();
});
