import { ArLooperPage } from "../pages/ArLooperPage";
import { AudioStudioPage } from "../pages/AudioStudioPage";
import { HomePage } from "../pages/HomePage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { routes } from "./routes";

function currentPath() {
  return window.location.pathname.replace(/\/$/, "") || "/";
}

export function App() {
  const path = currentPath();

  if (path === routes.home) {
    return <HomePage />;
  }

  if (path === routes.audioStudio) {
    return <AudioStudioPage />;
  }

  if (path === routes.arLooper) {
    return <ArLooperPage />;
  }

  return <NotFoundPage />;
}
