import { registerRootComponent } from "expo";
import App from "./App";

// Entry tường minh (tránh vấn đề expo/AppEntry với symlink pnpm trong monorepo).
registerRootComponent(App);
