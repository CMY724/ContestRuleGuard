import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, vi } from "vitest";
import { ProjectPage } from "./ProjectPage";


const project = {
  id: "p1",
  name: "赛规通",
  competition_name: "全球校园人工智能算法精英大赛",
  competition_year: 2026,
  track: "算法创新赛",
  target_stage: "school" as const,
  created_at: "2026-07-16T08:00:00Z",
  updated_at: "2026-07-16T08:00:00Z",
};

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as Response;
}

afterEach(() => vi.unstubAllGlobals());

test("加载并展示已有项目", async () => {
  vi.stubGlobal("fetch", vi.fn().mockResolvedValue(jsonResponse([project])));
  render(<ProjectPage />);
  expect(
    await screen.findByRole("heading", { name: "赛规通" }),
  ).toBeInTheDocument();
  expect(screen.getByText("2026 · 算法创新赛 · 校赛")).toBeInTheDocument();
});

test("初始列表加载完成前禁用项目创建", async () => {
  let resolveList!: (response: Response) => void;
  const pendingList = new Promise<Response>((resolve) => {
    resolveList = resolve;
  });
  vi.stubGlobal("fetch", vi.fn().mockReturnValue(pendingList));
  render(<ProjectPage />);

  const createButton = screen.getByRole("button", { name: "创建项目" });
  expect(createButton).toBeDisabled();

  resolveList(jsonResponse([]));
  expect(await screen.findByText("还没有项目")).toBeInTheDocument();
  expect(createButton).toBeEnabled();
});

test("初始列表加载失败时只显示错误而不显示空列表", async () => {
  vi.stubGlobal(
    "fetch",
    vi.fn().mockRejectedValue(new Error("project list unavailable")),
  );
  render(<ProjectPage />);

  expect(await screen.findByRole("alert")).toHaveTextContent(
    "project list unavailable",
  );
  expect(screen.queryByText("还没有项目")).not.toBeInTheDocument();
});

test("提交 snake_case 载荷并把新项目加入列表", async () => {
  const fetchMock = vi
    .fn<typeof fetch>()
    .mockResolvedValueOnce(jsonResponse([]))
    .mockResolvedValueOnce(jsonResponse(project, 201));
  vi.stubGlobal("fetch", fetchMock);
  const user = userEvent.setup();
  render(<ProjectPage />);

  await screen.findByText("还没有项目");
  await user.type(screen.getByLabelText("项目名称"), "赛规通");
  await user.type(
    screen.getByLabelText("比赛名称"),
    "全球校园人工智能算法精英大赛",
  );
  await user.clear(screen.getByLabelText("比赛年份"));
  await user.type(screen.getByLabelText("比赛年份"), "2026");
  await user.type(screen.getByLabelText("参赛赛道"), "算法创新赛");
  await user.selectOptions(screen.getByLabelText("目标阶段"), "school");
  await user.click(screen.getByRole("button", { name: "创建项目" }));

  expect(
    await screen.findByRole("heading", { name: "赛规通" }),
  ).toBeInTheDocument();
  const createRequest = fetchMock.mock.calls[1];
  const requestInit = createRequest[1] as RequestInit;
  expect(JSON.parse(String(requestInit.body))).toEqual({
    name: "赛规通",
    competition_name: "全球校园人工智能算法精英大赛",
    competition_year: 2026,
    track: "算法创新赛",
    target_stage: "school",
  });
});
