import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './App';

beforeEach(() => {
  // default fetch mock
  global.fetch = jest.fn((url) => {
    if (url.includes('/api/solutions')) {
      return Promise.resolve({ json: () => Promise.resolve({ results: [] }) });
    }
    if (url.endsWith('/data/solutions_combined.csv') || url.endsWith('solutions_combined.csv')) {
      return Promise.resolve({ text: () => Promise.resolve('name,category\nTest,Demo') });
    }
    return Promise.resolve({ json: () => Promise.resolve({}) });
  });
});

test('renders basic UI and preview combined CSV', async () => {
  render(<App />);
  expect(screen.getByText(/Climate Solutions/i)).toBeInTheDocument();

  const previewBtn = screen.getByText(/Preview Combined CSV/i);
  fireEvent.click(previewBtn);

  await waitFor(() => expect(global.fetch).toHaveBeenCalled());
  expect(screen.getByText(/Combined CSV preview/i)).toBeInTheDocument();
});

test('runs scraper trigger endpoint', async () => {
  global.fetch = jest.fn(() => Promise.resolve({ status: 200 }));
  render(<App />);
  const runBtn = screen.getByText(/Run Scraper/i);
  fireEvent.click(runBtn);
  await waitFor(() => expect(global.fetch).toHaveBeenCalled());
});
