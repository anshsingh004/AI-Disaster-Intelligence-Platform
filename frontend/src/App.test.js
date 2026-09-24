import { render, screen } from '@testing-library/react';
import Sidebar from './components/Sidebar';

test('renders Terra-Aura brand in sidebar', () => {
  render(<Sidebar active="dashboard" onNavigate={() => {}} />);
  const brandElement = screen.getByText(/Terra-Aura/i);
  expect(brandElement).toBeInTheDocument();
});

