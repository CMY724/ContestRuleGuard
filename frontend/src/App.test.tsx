import { render, screen } from "@testing-library/react";
import { afterEach, vi } from "vitest";
import App from "./App";

afterEach(() => vi.unstubAllGlobals());

test("显示赛规通产品定位", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [],
    } as Response),
  );
  render(<App />);
  expect(screen.getByRole("heading", { name: "赛规通" })).toBeInTheDocument();
  expect(screen.getByText("证据图驱动的竞赛合规智能体")).toBeInTheDocument();
  expect(await screen.findByText("还没有项目")).toBeInTheDocument();
});
