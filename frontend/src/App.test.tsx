import { render, screen } from "@testing-library/react";
import App from "./App";

test("显示赛规通产品定位", () => {
  render(<App />);
  expect(screen.getByRole("heading", { name: "赛规通" })).toBeInTheDocument();
  expect(screen.getByText("证据图驱动的竞赛合规智能体")).toBeInTheDocument();
});
