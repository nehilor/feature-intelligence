import { BrowserRouter, Route, Routes } from 'react-router-dom'

import { Layout } from './components/Layout'
import { DiscoverPage } from './pages/DiscoverPage'
import { DetailPage } from './pages/DetailPage'
import { SubmitPage } from './pages/SubmitPage'
import './App.css'

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<DiscoverPage />} />
          <Route path="/requests/new" element={<SubmitPage />} />
          <Route path="/requests/:requestId" element={<DetailPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}
