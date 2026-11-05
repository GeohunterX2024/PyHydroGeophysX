<?xml version='1.0' encoding='utf-8'?>
<TS version="2.1" language="zh_CN">
  <context>
    <name>PHGX</name>
    <message>
      <source>The AI assistant you are talking to</source>
      <extracomment>Appended to the rules when the assistant has written procedures (skills, :mod:`PyHydroGeophysX.agents.skills`): the index only; read_skill reads one. Appended to the rules only when the selected model reads images, so a text-only model is never told about a tool it will not be given. Name of the tool that hands a step-by-step task to Auto to report. The panel runs it itself, not the studio controller: it needs the provider settings, and it ends the step-by-step turn instead of adding a step to it. Name of the tool that proposes a temporary script. Run by the panel, after the user has read it and approved, in a process of its own. Tools that only look. They run at once, whatever the model says. Page actions that only look or show, by name. Page actions that throw away a set of the user's work (picks corrected by hand, electrodes, inputs): always the user's call. remove_air_wave and the like are filters, not removals, and stay with the model. Page actions that write files. Where the model names the destination, the user sees it before anything is written there. With no "ask_user" from the model: actions that start a long computation ask. Calls in a row the assistant may run without the user; the next one asks. A guard against a loop, not a budget: a task normally ends well before it. The answer to a call the user's Stop came before. Problems in a row - an automatic run that failed or fell short, a background job that failed - handed to the assistant without the user saying anything in between; after that the chat waits for the user. What the assistant is told when a job it started in the background failed. What the assistant is told when a page reported an error outside its own calls. Model replies that could not be used, asked for again before giving up. A failed model call that asking again would not fix: access, quota, limits. What the assistant is told when an automatic run failed or fell short.</extracomment>
      <translation>当前对话的 AI 助手</translation>
    </message>
    <message>
      <source>Settings</source>
      <translation>设置</translation>
    </message>
    <message>
      <source>Provider, model, API key, and the RAG / MCP switches</source>
      <translation>提供商、模型、API 密钥以及 RAG / MCP 开关</translation>
    </message>
    <message>
      <source>New chat</source>
      <translation>新建对话</translation>
    </message>
    <message>
      <source>Reject</source>
      <translation>剔除</translation>
    </message>
    <message>
      <source>Approve &amp; run</source>
      <translation>批准并运行</translation>
    </message>
    <message>
      <source>Step by step</source>
      <translation>逐步</translation>
    </message>
    <message>
      <source>Auto to report</source>
      <translation>自动至报告</translation>
    </message>
    <message>
      <source>Files shared with the assistant; RAG references are searched when RAG is enabled.</source>
      <translation>与助手共享的文件；启用 RAG 时会检索 RAG 参考资料。</translation>
    </message>
    <message>
      <source>Remove</source>
      <translation>移除</translation>
    </message>
    <message>
      <source>e.g. Build a 3D crosshole mesh with 12 sensors per borehole</source>
      <translation>例如：构建每个钻孔 12 个电极的三维跨孔网格</translation>
    </message>
    <message>
      <source>Send</source>
      <translation>发送</translation>
    </message>
    <message>
      <source>Paste or drop files · Ctrl+Enter to send</source>
      <translation>粘贴或拖放文件 · Ctrl+Enter 发送</translation>
    </message>
    <message>
      <source>Stop</source>
      <translation>停止</translation>
    </message>
    <message>
      <source>Stop the assistant after the action in hand. Anything already running on a page carries on there.</source>
      <translation>在当前操作完成后停止助手。页面上已在运行的任务会继续运行。</translation>
    </message>
    <message>
      <source>Level</source>
      <translation>级别</translation>
    </message>
    <message>
      <source>Custom model</source>
      <translation>自定义模型</translation>
    </message>
    <message>
      <source>Provider</source>
      <translation>提供商</translation>
    </message>
    <message>
      <source>Model</source>
      <extracomment>The model drawn on the Model and Layers views: its pyGIMLi mesh, the resistivity (n_cells, n_time), markers, coverage and cell outlines. Per marker, the (mean, std) last set in a panel; kept for a layer switched off, so switching it back on restores them. Why the last run did not finish - its error, or that it was stopped - for the assistant, whose status would otherwise still show the result before it; "" while a run is under way or succeeded.</extracomment>
      <translation>模型</translation>
    </message>
    <message>
      <source>Base URL</source>
      <translation>基础 URL</translation>
    </message>
    <message>
      <source>https://api.example.com/v1</source>
      <translation>https://api.example.com/v1</translation>
    </message>
    <message>
      <source>Paste API key for this session</source>
      <translation>粘贴本会话使用的 API 密钥</translation>
    </message>
    <message>
      <source>Apply</source>
      <translation>应用</translation>
    </message>
    <message>
      <source>Log in</source>
      <translation>登录</translation>
    </message>
    <message>
      <source>Retry</source>
      <translation>重试</translation>
    </message>
    <message>
      <source>Run the CLI setup again.</source>
      <translation>请重新运行 CLI 设置。</translation>
    </message>
    <message>
      <source>Cancel</source>
      <translation>取消</translation>
    </message>
    <message>
      <source>Stop waiting for the browser sign-in.</source>
      <translation>停止等待浏览器登录。</translation>
    </message>
    <message>
      <source>Reasoning</source>
      <translation>推理</translation>
    </message>
    <message>
      <source>How hard the model thinks before answering. Follows the level until you change it, then stays where you put it. Chat pays this on every tool call, so a high effort is felt one step at a time. Applies to reasoning models; not a display of private chain-of-thought.</source>
      <translation>模型在回答前的思考强度。在您更改之前跟随该级别，更改后保持您设定的值。对话中每次工具调用都会产生此开销，因此高强度会在每一步中都有所体现。适用于推理模型；并不显示私有的思维链。</translation>
    </message>
    <message>
      <source>RAG</source>
      <translation>RAG</translation>
    </message>
    <message>
      <source>Retrieve relevant excerpts from local documentation and selected reference files; record sources in the report.</source>
      <translation>从本地文档和所选参考文件中检索相关摘录；在报告中记录来源。</translation>
    </message>
    <message>
      <source>MCP</source>
      <translation>MCP</translation>
    </message>
    <message>
      <source>Connect to the bundled stdio MCP server and retrieve available workflow APIs. Requires the mcp extra.</source>
      <translation>连接内置的 stdio MCP 服务器并获取可用的工作流 API。需要安装 mcp 扩展。</translation>
    </message>
    <message>
      <source>Paste {0} for this session</source>
      <translation>粘贴本会话使用的 {0}</translation>
    </message>
    <message>
      <source>Log out</source>
      <translation>退出登录</translation>
    </message>
    <message>
      <source>Sign {0} out on this computer. To use another account, log out, then log in.</source>
      <translation>在此计算机上注销 {0}。如需使用其他账户，请先注销再登录。</translation>
    </message>
    <message>
      <source>Sign in with your subscription account in the browser.</source>
      <translation>在浏览器中使用订阅账户登录。</translation>
    </message>
    <message>
      <source>Log out of {0}?

This signs {1} out on this computer, including where you use it in a terminal. You can log in again here.</source>
      <translation>退出 {0} 登录？

这将在本机上退出 {1} 的登录，包括在终端中的使用。您可以在此处重新登录。</translation>
    </message>
    <message>
      <source>{0}{1} · {2} — ready{3}{4}</source>
      <translation>{0}{1} · {2} — 就绪{3}{4}</translation>
    </message>
    <message>
      <source>Local numerical tasks are ready · Configure AI only for interpretation</source>
      <translation>本地数值计算任务已就绪 · 仅在解释时需要配置 AI</translation>
    </message>
    <message>
      <source>Run the whole task and write the report without stopping.</source>
      <translation>不间断地运行整个任务并撰写报告。</translation>
    </message>
    <message>
      <source>Auto to report with {0} runs on {1}; choose one of those in Settings.</source>
      <translation>使用 {0} 时，“自动至报告”在 {1} 上运行；请在设置中选择其中之一。</translation>
    </message>
    <message>
      <source>{0} does the routine steps itself and asks you at the decisions. Ask for the final result at any point and the rest runs automatically.</source>
      <translation>{0} 会自行完成常规步骤，并在需要决策时询问您。可随时要求输出最终结果，其余步骤将自动运行。</translation>
    </message>
    <message>
      <source>&lt;b&gt;How should {0} carry this out?&lt;/b&gt;&lt;br&gt;Step by step, it does the routine steps itself, asks you at the decisions, and you can ask for the final result at any point. Auto to report runs straight through to the report.</source>
      <translation>&lt;b&gt;{0} 应如何执行？&lt;/b&gt;&lt;br&gt;逐步执行：常规步骤自动完成，遇到决策时询问您，并可随时要求给出最终结果。自动至报告：一直运行到生成报告。</translation>
    </message>
    <message>
      <source>Run this script</source>
      <translation>运行此脚本</translation>
    </message>
    <message>
      <source>Conceptual subsurface illustration — not measured data</source>
      <extracomment>The model-data loop, one card per navigator group, in the order the loop runs: (direction, title, what it does, tree group). Below these widths of Home the illustration goes, the title steps down and the project actions move under the project name.</extracomment>
      <translation>地下概念示意图——非实测数据</translation>
    </message>
    <message>
      <source>Session details</source>
      <translation>会话详情</translation>
    </message>
    <message>
      <source>Let {0} plan, run and explain your research workflow.</source>
      <translation>让 {0} 规划、运行并解释您的研究工作流。</translation>
    </message>
    <message>
      <source>PyHydroGeophysX Studio: unexpected error</source>
      <translation>PyHydroGeophysX Studio：意外错误</translation>
    </message>
    <message>
      <source>An unexpected error occurred. The application will try to keep running; details are below.</source>
      <translation>发生意外错误。应用程序将尝试继续运行；详细信息如下。</translation>
    </message>
    <message>
      <source>Assistant</source>
      <translation>助手</translation>
    </message>
    <message>
      <source>Properties</source>
      <translation>属性</translation>
    </message>
    <message>
      <source>Ready</source>
      <translation>就绪</translation>
    </message>
    <message>
      <source>Project: (none)</source>
      <extracomment>"Use Default Folder" was the answer this session; the next asks again.</extracomment>
      <translation>工程：（无）</translation>
    </message>
    <message>
      <source>Results go to the current working directory.</source>
      <translation>结果写入当前工作目录。</translation>
    </message>
    <message>
      <source>Project folder</source>
      <translation>工程文件夹</translation>
    </message>
    <message>
      <source>{0} cannot be written to:
{1}</source>
      <translation>{0} 无法写入：
{1}</translation>
    </message>
    <message>
      <source>&amp;File</source>
      <translation>文件(&amp;F)</translation>
    </message>
    <message>
      <source>New Project…</source>
      <translation>新建工程…</translation>
    </message>
    <message>
      <source>Open Project…</source>
      <translation>打开工程…</translation>
    </message>
    <message>
      <source>Import Existing Results…</source>
      <translation>导入已有结果…</translation>
    </message>
    <message>
      <source>Save Runs to Project</source>
      <translation>将运行保存到工程</translation>
    </message>
    <message>
      <source>Add this session's finished runs to the Project's history. Nothing is recorded there until you do.</source>
      <translation>将本会话已完成的运行添加到工程历史记录。执行此操作前不会记录任何内容。</translation>
    </message>
    <message>
      <source>Discard Unsaved Runs…</source>
      <translation>放弃未保存的运行…</translation>
    </message>
    <message>
      <source>Export Results…</source>
      <translation>导出结果…</translation>
    </message>
    <message>
      <source>Write the current module's results to a folder you choose, CSV included.</source>
      <translation>将当前模块的结果（含 CSV）写入所选文件夹。</translation>
    </message>
    <message>
      <source>Streamlit Bridge</source>
      <translation>Streamlit 桥接</translation>
    </message>
    <message>
      <source>Open Project Context…</source>
      <translation>打开工程上下文…</translation>
    </message>
    <message>
      <source>Save Studio Result</source>
      <translation>保存 Studio 结果</translation>
    </message>
    <message>
      <source>Export Module Result (JSON)…</source>
      <translation>导出模块结果 (JSON)…</translation>
    </message>
    <message>
      <source>Rebuild Run Index</source>
      <translation>重建运行索引</translation>
    </message>
    <message>
      <source>Exit</source>
      <translation>退出</translation>
    </message>
    <message>
      <source>&amp;View</source>
      <translation>视图(&amp;V)</translation>
    </message>
    <message>
      <source>Reset Layout</source>
      <translation>重置布局</translation>
    </message>
    <message>
      <source>Length Units</source>
      <translation>长度单位</translation>
    </message>
    <message>
      <source>Show distances, elevations and depths on every plot in {0}. The data themselves stay in metres.</source>
      <translation>在所有图件中以 {0} 显示距离、高程和深度。数据本身仍以米为单位。</translation>
    </message>
    <message>
      <source>Appearance</source>
      <translation>外观</translation>
    </message>
    <message>
      <source>Language</source>
      <translation>语言</translation>
    </message>
    <message>
      <source>Show all processing tools</source>
      <translation>显示所有处理工具</translation>
    </message>
    <message>
      <source>&amp;Tools</source>
      <translation>工具(&amp;T)</translation>
    </message>
    <message>
      <source>Model Viewer</source>
      <translation>模型查看器</translation>
    </message>
    <message>
      <source>Geophysical Data Processing</source>
      <translation>地球物理数据处理与反演</translation>
    </message>
    <message>
      <source>Hydro → Geophysics</source>
      <translation>水文 → 地球物理</translation>
    </message>
    <message>
      <source>Geophy → Hydrology</source>
      <translation>地球物理 → 水文</translation>
    </message>
    <message>
      <source>Seismic → Structure</source>
      <translation>地震 → 构造</translation>
    </message>
    <message>
      <source>ERT → Water Content</source>
      <translation>ERT → 含水量</translation>
    </message>
    <message>
      <source>&amp;Help</source>
      <translation>帮助(&amp;H)</translation>
    </message>
    <message>
      <source>Environment Check…</source>
      <translation>环境检查…</translation>
    </message>
    <message>
      <source>About</source>
      <translation>关于</translation>
    </message>
    <message>
      <source>Show or hide the project panel</source>
      <extracomment>Longest activity phrase the status bar shows; the label never wraps, and a long one would push the output folder off the bar.</extracomment>
      <translation>显示或隐藏左侧工程区</translation>
    </message>
    <message>
      <source>{0} — the run button of the step on screen</source>
      <translation>{0} — 即当前步骤的运行按钮</translation>
    </message>
    <message>
      <source>Open Project</source>
      <translation>打开工程</translation>
    </message>
    <message>
      <source>Save</source>
      <translation>保存</translation>
    </message>
    <message>
      <source>Pan</source>
      <translation>平移</translation>
    </message>
    <message>
      <source>Zoom</source>
      <translation>缩放</translation>
    </message>
    <message>
      <source>Pick</source>
      <translation>拾取</translation>
    </message>
    <message>
      <source>Delete</source>
      <translation>删除</translation>
    </message>
    <message>
      <source>Module: {0}</source>
      <translation>模块：{0}</translation>
    </message>
    <message>
      <source>Working…</source>
      <translation>正在处理…</translation>
    </message>
    <message>
      <source>Save Runs to Project (Ctrl+S)</source>
      <translation>将运行保存到工程（Ctrl+S）</translation>
    </message>
    <message>
      <source>Export Results… (Ctrl+E)</source>
      <translation>导出结果…（Ctrl+E）</translation>
    </message>
    <message>
      <source>Pan: drag to move the plot</source>
      <translation>平移：拖动以移动图件</translation>
    </message>
    <message>
      <source>Zoom: drag a box to zoom into it</source>
      <translation>缩放：拖出方框放大该区域</translation>
    </message>
    <message>
      <source>Pick: click a section to place a marker</source>
      <translation>拾取：在剖面上单击放置标记</translation>
    </message>
    <message>
      <source>Show or hide the assistant panel</source>
      <extracomment>The page button the toolbar's Run repeats, or None.</extracomment>
      <translation>显示或隐藏右侧助手区</translation>
    </message>
    <message>
      <source>Quit the Studio (Ctrl+Q)</source>
      <translation>退出软件（Ctrl+Q）</translation>
    </message>
    <message>
      <source> (+{0})</source>
      <translation>（另 {0} 项）</translation>
    </message>
    <message>
      <source>Working: {0}</source>
      <translation>正在处理：{0}</translation>
    </message>
    <message>
      <source>Click to open the page.</source>
      <translation>单击打开该页面。</translation>
    </message>
    <message>
      <source>Independent processing tool · These settings do not change the {0} workflow. Use Data &amp; reports → Data to edit and check its run configuration.</source>
      <translation>独立处理工具 · 这些设置不会改变 {0} 工作流。请使用“数据与报告 → 数据”编辑并检查其运行配置。</translation>
    </message>
    <message>
      <source>● {0} unsaved run{1}</source>
      <translation>● {0} 个未保存的运行</translation>
    </message>
    <message>
      <source>Save runs</source>
      <translation>保存运行</translation>
    </message>
    <message>
      <source>Discard unsaved runs</source>
      <translation>放弃未保存的运行</translation>
    </message>
    <message>
      <source>Permanently delete {0} unsaved run folder(s)?

Their inputs, outputs, and logs go with them. This cannot be undone.</source>
      <translation>永久删除 {0} 个未保存的运行文件夹？

其输入、输出和日志将一并删除。此操作无法撤销。</translation>
    </message>
    <message>
      <source>Discard runs</source>
      <translation>放弃运行</translation>
    </message>
    <message>
      <source>Unsaved runs</source>
      <translation>未保存的运行</translation>
    </message>
    <message>
      <source>Unsaved runs from an earlier session</source>
      <translation>先前会话中未保存的运行</translation>
    </message>
    <message>
      <source>Recover</source>
      <translation>恢复</translation>
    </message>
    <message>
      <source>Not now</source>
      <translation>暂不</translation>
    </message>
    <message>
      <source>Export results</source>
      <translation>导出结果</translation>
    </message>
    <message>
      <source>{0} can export:</source>
      <translation>{0} 可导出：</translation>
    </message>
    <message>
      <source>Save Project</source>
      <translation>保存工程</translation>
    </message>
    <message>
      <source>Import existing results folder</source>
      <translation>导入已有结果文件夹</translation>
    </message>
    <message>
      <source>Import existing results</source>
      <translation>导入已有结果</translation>
    </message>
    <message>
      <source>No explicit workflow recipe/result pairs were found. No files were changed.</source>
      <translation>未找到明确的工作流配方/结果对。未更改任何文件。</translation>
    </message>
    <message>
      <source>Found {0} recipe/result pair(s). Add run metadata without moving the scientific files?</source>
      <translation>找到 {0} 组配方/结果对。是否在不移动科学数据文件的情况下添加运行元数据？</translation>
    </message>
    <message>
      <source>Open project context</source>
      <translation>打开工程上下文</translation>
    </message>
    <message>
      <source>Save failed</source>
      <translation>保存失败</translation>
    </message>
    <message>
      <source>Result saved</source>
      <translation>结果已保存</translation>
    </message>
    <message>
      <source>Studio result written to:
{0}</source>
      <translation>Studio 结果已写入：
{0}</translation>
    </message>
    <message>
      <source>Export module result</source>
      <translation>导出模块结果</translation>
    </message>
    <message>
      <source>The new language is used the next time the Studio starts.</source>
      <translation>新语言将在下次启动 Studio 时生效。</translation>
    </message>
    <message>
      <source>Environment Check - {0}</source>
      <translation>环境检查 - {0}</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0}&lt;/b&gt;&lt;br&gt;&lt;br&gt;Local desktop companion to the PyHydroGeophysX Streamlit app for professional geophysical mouse interaction: data processing, hydro-to-geophysics profile selection, picking, and forward modeling.</source>
      <translation>&lt;b&gt;{0}&lt;/b&gt;&lt;br&gt;&lt;br&gt;PyHydroGeophysX Streamlit 应用的本地桌面配套程序，提供专业的地球物理鼠标交互：数据处理、水文至地球物理剖面选取、拾取与正演模拟。</translation>
    </message>
    <message>
      <source>The workflow runs in its own process and writes to the run folder; this panel's own controls are untouched.</source>
      <extracomment>One offer in a module's export menu: what it writes, and how to write it. What counts as something the user can be shown mid-run. Scaled figure thumbnails, newest use last, keyed by (path, mtime, size, height). A run's figures are saved at print resolution - five to six thousand pixels across - and decoding a full-size file to show it 96 px high costs UI-thread time, so the activity strip decodes each figure once and reuses the thumbnail whenever its figure list changes. Enough for several runs' strips; one entry is at most a few hundred KB. Page log levels (``BaseModule.log``) as logging levels; others are INFO. The activity of a page whose running workers say nothing more specific. A count such as "12/418" that a progress line already carries. Who is told of every error the studio's pages report (:func:`watch_errors`).</extracomment>
      <translation>工作流在独立进程中运行并写入运行文件夹；本面板的控件不受影响。</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0} is waiting for you&lt;/b&gt;&lt;br&gt;{1}</source>
      <extracomment>Whether a question is on screen here awaiting an answer.</extracomment>
      <translation>&lt;b&gt;{0} 正在等待您&lt;/b&gt;&lt;br&gt;{1}</translation>
    </message>
    <message>
      <source>{0}
Click to open full size.</source>
      <extracomment>What the agent is doing. One vocabulary for every widget in this module. States in which the agent is actively doing something, which is what the passing light on text means. Waiting is shown by a steady pulse instead. The palette entry each state's text is drawn in. The full-strength colour each finished or paused state is marked with. Neutral grey that reads on both appearances, for marks inside rich text. Longest a line takes to write out, however long it is: the display must never fall behind the run it is describing. How long a finished run's glow lingers, then fades.</extracomment>
      <translation>{0}
单击以原尺寸打开。</translation>
    </message>
    <message>
      <source>Add to Map…</source>
      <extracomment>Ask the main window to open the Mesh 3D module and load a mesh/volume file. Ask the main window to switch to another module by key (cross-module handoff). Ask the main window to open another module and apply one of its ``agent_apply`` actions there: ``(module key, action, args)``. How a page hands its work to another, such as the ERT page's electrodes to the 3D Mesh Builder and the mesh built there back. What the page is busy with changed: the new :meth:`activity`, "" once idle. Attribute names of the page's run buttons, one per step: the main toolbar's Run repeats the one on screen (:meth:`toolbar_run_buttons`). What each registered worker is doing, by id(): the phrase it was registered with, then its latest progress line. Work on the GUI thread the page announced itself (set_activity). time.monotonic() when the page last went from idle to busy. (handle, operation, RunLog, closing) for each run whose log is open. The lines logged in the current event-loop turn, so a run started in it keeps what was logged while it was being prepared. ``(message, level)`` callables told every line the page logs.</extracomment>
      <translation>添加到地图…</translation>
    </message>
    <message>
      <source>Save this recovered result as a survey in Project Map. Confirm its location before adding.</source>
      <translation>将此恢复结果作为测量保存到工程地图。添加前请确认其位置。</translation>
    </message>
    <message>
      <source>Result ready</source>
      <translation>结果就绪</translation>
    </message>
    <message>
      <source>Add this result to Project Map?</source>
      <translation>将此结果添加到工程地图？</translation>
    </message>
    <message>
      <source>Load the wells, logs and water levels here. Add them to the Project Map to compare each well with the surveys around it.</source>
      <translation>在此载入钻孔、测井曲线和水位。将其添加到工程地图，以便将每个钻孔与周围的测量进行比较。</translation>
    </message>
    <message>
      <source>Show</source>
      <translation>显示</translation>
    </message>
    <message>
      <source>Ticked wells are drawn on the Logs and Water levels views and highlighted on the map; click a well on the map to tick it.</source>
      <translation>勾选的钻孔将绘制在“测井曲线”和“水位”视图中，并在地图上高亮显示；点击地图上的钻孔即可勾选。</translation>
    </message>
    <message>
      <source>Range of all readings</source>
      <translation>所有读数的范围</translation>
    </message>
    <message>
      <source>Nearest to a date</source>
      <translation>最接近某日期</translation>
    </message>
    <message>
      <source>Water level on the logs</source>
      <translation>测井曲线上的水位</translation>
    </message>
    <message>
      <source>Date</source>
      <translation>日期</translation>
    </message>
    <message>
      <source>Project Map</source>
      <translation>工程地图</translation>
    </message>
    <message>
      <source>Put the wells on the Project Map with their logs and water levels. There, clicking a well sets its log beside every survey around it.</source>
      <translation>将钻孔连同其测井曲线和水位放到工程地图上。在地图上点击钻孔，即可将其测井曲线显示在周围每次勘探旁。</translation>
    </message>
    <message>
      <source>Add wells to the Map…</source>
      <translation>将钻孔添加到地图…</translation>
    </message>
    <message>
      <source>Save the wells, their logs and water levels as a layer of the Project Map. Adding them again after an edit adds the new version.</source>
      <translation>将钻孔及其测井曲线和水位保存为工程地图的一个图层。编辑后再次添加会加入新版本。</translation>
    </message>
    <message>
      <source>Depth to water</source>
      <translation>水位埋深</translation>
    </message>
    <message>
      <source>View:</source>
      <extracomment>Width the control panel may not exceed even if its widest row wants more. Past this the row scrolls rather than eating the space the section needs. ``(first_station, x, y)`` of the running line inversion: the map coordinates the section is given when it comes back (_attach_line_xy). ``(key, soundings)``: every sounding of the loaded survey, read once on a worker thread under the load settings ``key`` names. Station changes, the observed-data resource and Run are served from it, so none of them walks the file again (see _ensure_survey).</extracomment>
      <translation>视图：</translation>
    </message>
    <message>
      <source>View the recovered section or volume, and - for a survey of several lines - resistivity kriged in plan view at several depths with its kriging uncertainty. Use Add to Map for interactive depth slices in Project Map.</source>
      <translation>查看反演得到的断面或三维体；对于多条测线的测量，还可查看多个深度处平面克里金插值的电阻率及其克里金不确定度。使用“添加到地图”可在工程地图中交互查看深度切片。</translation>
    </message>
    <message>
      <source>Sounding</source>
      <translation>测深</translation>
    </message>
    <message>
      <source>Survey and QC</source>
      <translation>测量与质量控制</translation>
    </message>
    <message>
      <source>Signal and noise</source>
      <translation>信号与噪声</translation>
    </message>
    <message>
      <source>Resistivity model</source>
      <translation>电阻率模型</translation>
    </message>
    <message>
      <source>Inversion quality</source>
      <translation>反演质量</translation>
    </message>
    <message>
      <source>Load sounding data</source>
      <extracomment>View entries after the section and the volume, while a survey's maps are drawn.</extracomment>
      <translation>载入测深数据</translation>
    </message>
    <message>
      <source>Method</source>
      <translation>方法</translation>
    </message>
    <message>
      <source>Data format</source>
      <translation>数据格式</translation>
    </message>
    <message>
      <source>Load data…</source>
      <translation>载入数据…</translation>
    </message>
    <message>
      <source>Format help</source>
      <translation>格式帮助</translation>
    </message>
    <message>
      <source>LM+HM fits all available gates to one shared model. HM uses later-time gates and LM uses early-time gates. In-use flags are applied automatically.</source>
      <translation>LM+HM 用一个共享模型拟合所有可用时窗。HM 使用晚期时窗，LM 使用早期时窗。使用标志将自动应用。</translation>
    </message>
    <message>
      <source>Moment(s)</source>
      <translation>磁矩</translation>
    </message>
    <message>
      <source>Use the project's in-use flags</source>
      <translation>使用工程中的“在用”标记</translation>
    </message>
    <message>
      <source>On: only the gates the project file marks as in use are imported.

Off: every gate holding a finite, non-dummy value is imported, including those the project marks unused. On a noisy survey that can be several times as many gates. Each one keeps its recorded stack error, so its weight in the fit is unchanged.</source>
      <translation>开：仅导入工程文件标记为使用中的时窗。

关：导入所有包含有限非虚设值的时窗，包括工程标记为未使用的时窗。对于噪声较大的勘探，时窗数量可能是原来的数倍。每个时窗保留其记录的叠加误差，因此其在拟合中的权重不变。</translation>
    </message>
    <message>
      <source>off</source>
      <translation>关</translation>
    </message>
    <message>
      <source>Condemns a gate whose relative stack error exceeds this value, and (unless sign reversals are kept below) one whose value is negative.

The stack error is the scatter of the repeat transients divided by their mean, so a gate near or above 0.3 disagrees with itself by as much as the quantity being measured.

0 turns the cut off entirely.</source>
      <translation>剔除相对叠加误差超过此值的时窗，以及（除非下方设置保留符号反转）取值为负的时窗。

叠加误差为重复瞬变的离散度除以其均值，因此接近或超过 0.3 的时窗，其自身偏差与被测量值相当。

设为 0 则完全关闭该截断。</translation>
    </message>
    <message>
      <source>Tail cut (σ)</source>
      <translation>尾部截断 (σ)</translation>
    </message>
    <message>
      <source>What a failed stack-error test above removes. It governs that test only: a sign reversal always costs its own gate and no other.

Truncate the tail: the first failing gate ends the sounding and every later gate goes with it. Safe, because past the first bad gate the decay has usually fallen into the noise.

Reject gates individually: only the failing gates are dropped and the later ones are kept. Diffusion depth grows with time, so the latest usable gate sets how deep the sounding can see; this keeps it when a neighbour is spoiled by a local interference spike, at the risk of keeping a gate that looks clean by chance.</source>
      <translation>上方叠加误差检验未通过时剔除的内容。仅作用于该检验：符号反转始终只剔除其自身所在的时窗，不影响其他时窗。

截断尾部：第一个未通过的时窗终止该测深，其后所有时窗一并剔除。此方式稳妥，因为在第一个坏时窗之后，衰减通常已落入噪声。

逐个剔除时窗：仅剔除未通过的时窗，保留其后的时窗。扩散深度随时间增大，因此最晚的可用时窗决定测深的探测深度；当相邻时窗被局部干扰尖峰破坏时，此方式可保留该时窗，但有可能保留偶然看似干净的时窗。</translation>
    </message>
    <message>
      <source>Cut removes</source>
      <translation>截断剔除</translation>
    </message>
    <message>
      <source>Keep sign reversals</source>
      <translation>保留符号反转</translation>
    </message>
    <message>
      <source>On (the default): a negative gate is judged on its stack error alone. This is what the TEMcompany inversion does: its gate selection is exactly the stored in-use flags, and it keeps non-positive gates.

Off: a negative gate is condemned by its sign.

An offset-loop system genuinely reverses sign at early time, while the diffusing current system is still inside the transmitter-receiver offset. Whether that reversal reaches the gates being inverted has a number attached: the crossing sits near an induction number of one, so a gate at time t sees it only once the ground is more conductive than mu0*r^2/(4t). On a 15 m offset that is about 6 ohm-m at 12 us and 1 ohm-m at 61 us.

Turn this on where that expression says the reversal is real. Where it says the crossing falls far earlier than the first gate, a negative gate is something a layered earth cannot produce, and keeping it lets the fit trade the rest of the sounding against a value it can never reach.</source>
      <translation>开（默认）：负值时窗仅依据其叠加误差判断。这与 TEMcompany 反演的做法一致：其时窗选择严格按照存储的使用标记，并保留非正值时窗。

关：负值时窗因其符号而被剔除。

偏移回线系统在早期时间确实会出现符号反转，此时扩散的电流系统仍位于发射-接收偏移距之内。这种反转是否会影响参与反演的时窗，可以定量判断：过零点位于感应数约为 1 处，因此时间为 t 的时窗只有在大地电阻率低于 mu0*r^2/(4t) 时才会出现反转。在 15 m 偏移距下，12 us 时约为 6 ohm-m，61 us 时约为 1 ohm-m。

若该表达式表明反转真实存在，则开启此项。若表明过零点远早于第一个时窗，则负值时窗是层状大地无法产生的，保留它会使拟合为迁就一个永远无法达到的值而牺牲测深的其余部分。</translation>
    </message>
    <message>
      <source>Drops the deep (HM) moment from a station that survives gate selection with fewer than this many gates. LM is never dropped.

A moment reduced to one or two gates still costs a forward call and still enters the misfit, and two points cannot separate the level of a decay from its slope, so what it adds is a degree of freedom the fit absorbs rather than a constraint on the model.

Against that, the deep moment is the only thing that sees deep, so a station stripped of its HM keeps its shallow model and loses its depth. Which argument wins depends on the survey, so this is off by default. A station that has no LM gates either is left with no data at all.</source>
      <translation>若测点在时窗筛选后保留的时窗少于此数，则剔除其深部（HM）磁矩。LM 从不剔除。

只剩一两个时窗的磁矩仍需一次正演计算，仍计入拟合差，而两个点无法区分衰减的幅值与斜率，因此它增加的只是被拟合吸收的自由度，而非对模型的约束。

反之，深部磁矩是唯一能探测深部的数据，剔除 HM 的测点只保留浅部模型而失去深度。孰优孰劣取决于具体测量，因此默认关闭。若测点同时没有 LM 时窗，则将完全没有数据。</translation>
    </message>
    <message>
      <source>Min HM gates</source>
      <translation>最少 HM 时窗数</translation>
    </message>
    <message>
      <source>Auto-detect or select .gex</source>
      <translation>自动检测或选择 .gex</translation>
    </message>
    <message>
      <source>Browse…</source>
      <translation>浏览…</translation>
    </message>
    <message>
      <source>System GEX</source>
      <translation>系统 GEX</translation>
    </message>
    <message>
      <source>Auto-detect or select .tfi</source>
      <translation>自动检测或选择 .tfi</translation>
    </message>
    <message>
      <source>Import filter TFI</source>
      <translation>导入 TFI 滤波器</translation>
    </message>
    <message>
      <source>Load geometry…</source>
      <translation>载入几何…</translation>
    </message>
    <message>
      <source>Load a file of along-line positions (and optional sensor height), one row per sounding, so the section uses real distances instead of uniform spacing. See Data format.</source>
      <translation>载入沿测线位置文件（可选传感器高度），每个测深一行，使断面使用实际距离而非均匀间距。参见“数据格式”。</translation>
    </message>
    <message>
      <source>Geometry: uniform spacing.</source>
      <translation>几何：均匀间距。</translation>
    </message>
    <message>
      <source>Choose a data format, then load a file or project folder. FDEM: columns freq, real, imag. TDEM: columns time, response. Several soundings are inverted into a resistivity section/map.</source>
      <translation>选择数据格式，然后载入文件或工程文件夹。FDEM：列为 freq、real、imag。TDEM：列为 time、response。多个测深将反演为电阻率断面/平面图。</translation>
    </message>
    <message>
      <source>Selects which of the file's soundings the preview shows. A line inversion uses the whole survey regardless of this setting.</source>
      <translation>选择预览中显示文件中的哪个测深。无论此设置如何，测线反演都会使用整个测量。</translation>
    </message>
    <message>
      <source>Preview sounding #</source>
      <translation>预览测深 #</translation>
    </message>
    <message>
      <source>No sounding loaded.</source>
      <translation>未载入测深。</translation>
    </message>
    <message>
      <source>Survey geometry (system)</source>
      <translation>测量几何（系统）</translation>
    </message>
    <message>
      <source>Physical transmitter-loop area. For raw tTEM this also re-normalizes dB/dt by the chosen area, so changing it affects both data and forward model.</source>
      <translation>发射回线的实际面积。对于原始 tTEM 数据，还会按所选面积重新归一化 dB/dt，因此修改此值会同时影响数据和正演模型。</translation>
    </message>
    <message>
      <source>Distance from the transmitter loop to the receiver coil.

A walking ground survey records its own for every station, and those are used in preference to this while the box below is ticked. The separation varies from station to station around its nominal value, so a single number here cannot describe the survey; it is the value for a format that records none, and the override when the box is cleared.</source>
      <translation>发射回线到接收线圈的距离。

步行式地面测量会为每个测点记录各自的距离，勾选下方复选框时优先使用这些记录值。各测点的收发距在其标称值附近变化，因此此处单个数值无法描述整个测量；它用于未记录该距离的格式，并在取消勾选时作为覆盖值。</translation>
    </message>
    <message>
      <source>Height of the {0} above the ground. TEMcompany projects normally record the two equal, but the forward places them separately, so a frame that does not can say so.</source>
      <translation>{0}的离地高度。TEMcompany 工程通常将两者记录为相等，但正演会分别放置它们，因此两者不等的数据帧可在此说明。</translation>
    </message>
    <message>
      <source>Use each station's own recorded geometry</source>
      <translation>使用各测点自身记录的几何参数</translation>
    </message>
    <message>
      <source>A project records the separation and the two heights per station, and with this ticked those are what the run uses; the fields above then show the loaded station rather than the survey, and editing them changes nothing.

Clear it to impose the values above on every station. That is the honest way to test a suspect geometry column, and it is what a format recording no per-station geometry does anyway.

The separation is rounded to a quarter of a metre so that stations sharing a geometry share one warmed-up forward operator, which is well inside what the response can resolve.</source>
      <translation>工程记录了每个测点的收发距和两个高度；勾选此项时，运行将使用这些值；此时上方字段显示的是当前载入测点的值而非整个测量的值，编辑它们不会产生任何影响。

取消勾选则将上方的值强制应用于所有测点。这是检验可疑几何列的可靠方法，也是不记录逐测点几何信息的格式本来的处理方式。

收发距会取整到 0.25 m，以便几何相同的测点共享同一个已预热的正演算子，这远在响应可分辨的范围之内。</translation>
    </message>
    <message>
      <source>Which field the sounding's values are: the secondary field alone, or the total field including the primary. The inversion fits the one chosen.</source>
      <translation>测深值对应的场：仅二次场，或包含一次场的总场。反演将拟合所选的场。</translation>
    </message>
    <message>
      <source>Source radius (m)</source>
      <translation>源半径 (m)</translation>
    </message>
    <message>
      <source>Tx loop area (m²)</source>
      <translation>发射回线面积 (m²)</translation>
    </message>
    <message>
      <source>Tx-Rx sep (m)</source>
      <translation>收发间距 (m)</translation>
    </message>
    <message>
      <source>Height Tx / Rx (m)</source>
      <translation>Tx / Rx 高度 (m)</translation>
    </message>
    <message>
      <source>Orientation</source>
      <translation>方位</translation>
    </message>
    <message>
      <source>Component</source>
      <translation>分量</translation>
    </message>
    <message>
      <source>Waveform</source>
      <translation>波形</translation>
    </message>
    <message>
      <source>Inversion</source>
      <translation>反演</translation>
    </message>
    <message>
      <source>Ground TEM (TEM2Go, tTEM)</source>
      <translation>地面 TEM (TEM2Go, tTEM)</translation>
    </message>
    <message>
      <source>Generic / airborne</source>
      <translation>通用 / 航空</translation>
    </message>
    <message>
      <source>A starting point for the settings below, which stay editable.

Ground TEM carries what a walking ground survey was found to want: twenty layers over a hundred metres, fixed regularisation rather than a chi-square chase, robust errors keeping all imported gates, and a resistivity ceiling low enough that an unresolved deep layer cannot rail to 1e5 and be read as a measurement. It is applied automatically when a ground project is loaded.

Generic is the framework default, which has to serve an airborne line that sees several hundred metres as well as a ground sounding that sees thirty, so it is deliberately unopinionated.</source>
      <translation>为下方设置提供起点，各项仍可编辑。

地面 TEM 采用地面步行测量所需的设置：一百米内二十层、固定正则化而非追逐卡方目标、稳健误差并保留所有导入时窗，以及足够低的电阻率上限，使未分辨的深层不会顶到 1e5 而被误读为测量结果。载入地面工程时会自动应用。

通用为框架默认值，需同时适用于探测数百米的航空测线和仅探测三十米的地面测深，因此刻意保持中立。</translation>
    </message>
    <message>
      <source>Fixed layers in the model. The grid is shared by every sounding on a line, which is what lets them be coupled layer by layer.</source>
      <translation>模型中的固定层。同一测线上的所有测深共用该网格，因此可以逐层耦合。</translation>
    </message>
    <message>
      <source>auto</source>
      <translation>自动</translation>
    </message>
    <message>
      <source>Uniform resistivity assigned to every layer at the start of the inversion. It sets the optimizer's initial model and does not also supplies the reference for model damping.

auto tries a set of uniform half-spaces on a sample of the soundings and starts from the one whose forward response comes closest to the data. Where a run starts decides which minimum it settles in: the Gauss-Newton step is built from a linearization about the current model, so a start a decade away from the ground describes a different problem. On one ground survey the project's own 40 Ω·m default reached χ² 387 where auto reached 8.7, and the 40 Ω·m run drove a tenth of the section onto the 1 Ω·m bound.

A value uses that resistivity, which is what a project file carries. For a line inversion this seeds the first solve; later refinement passes warm-start from the preceding result.</source>
      <translation>反演开始时赋予每一层的均匀电阻率。它设定优化器的初始模型，但不同时作为模型阻尼的参考。

auto 会在部分测深样本上试算一组均匀半空间，并从正演响应最接近数据的那个开始。起点决定反演最终落入哪个极小值：Gauss-Newton 步长基于当前模型的线性化构建，因此与实际地层相差一个数量级的起点描述的是另一个问题。在某次地面测量中，工程自带的 40 Ω·m 默认值得到 χ² 387，而 auto 得到 8.7，且 40 Ω·m 的运行将十分之一的断面推到 1 Ω·m 下限上。

填写数值则使用该电阻率，工程文件中保存的即为此值。对于测线反演，此值作为首次求解的初值；后续细化轮次从上一结果热启动。</translation>
    </message>
    <message>
      <source>Vertical smoothness down each sounding's layer stack. Higher gives a smoother profile and fits the data less well.</source>
      <translation>沿每个测深点层序向下的垂直光滑度。值越大，剖面越光滑，但数据拟合越差。</translation>
    </message>
    <message>
      <source>Iteration budget for Gauss-Newton and independent 1D solves. Simultaneous TRF uses its separate forward-evaluation budget in the Line group.</source>
      <translation>Gauss-Newton 和独立一维求解的迭代次数上限。同步 TRF 使用“测线”组中单独的正演计算次数上限。</translation>
    </message>
    <message>
      <source>Cumulative sensitivity below which a cell is reported as unresolved.

The quantity is summed from the base of the model upward, and the deepest layer is the thickest, so a low threshold saturates: on one ground survey a threshold of 0.8 put the reported depth of investigation at the very bottom of the model for more than half the stations, which is the metric running out rather than the data reaching that deep. Six to eight keeps the reported depth inside the model.</source>
      <translation>累积灵敏度低于此值的单元将被报告为未分辨。

该量自模型底部向上累加，且最深层最厚，因此阈值过低会饱和：在某次地面测量中，阈值 0.8 使超过半数测点报告的探测深度位于模型最底部，这是指标失效所致，而非数据真正探测到如此深度。取 6 到 8 可使报告的深度保持在模型内部。</translation>
    </message>
    <message>
      <source>Preset</source>
      <translation>预设</translation>
    </message>
    <message>
      <source>Layers</source>
      <translation>层</translation>
    </message>
    <message>
      <source>Thickness</source>
      <translation>厚度</translation>
    </message>
    <message>
      <source>Initial model ρ (Ω·m)</source>
      <translation>初始模型 ρ (Ω·m)</translation>
    </message>
    <message>
      <source>The other half of the regularisation: how tightly neighbouring soundings on the same survey line are tied to each other, where Smoothness above ties the layers within one sounding. It applies to a line inversion only, never crosses a survey line, and 0 leaves the soundings independent whatever the coupling in the Line group says.

The tie does not weaken with distance at the spacings a ground survey walks: the weight falls off only once a pair is further apart than the reference distance, which defaults to 50 m, and is exactly 1 for anything closer.

A settings file may also carry lateral_weight_scale. That is a multiplier on this value rather than a second control, so the effective weight is the product of the two; it stays at 1.0 and this is the number to change.</source>
      <translation>正则化的另一半：同一测线上相邻测深之间的约束强度，而上方的“光滑度”约束的是单个测深内部的各层。它仅适用于测线反演，绝不跨越测线；设为 0 时各测深相互独立，无论“测线”组中的耦合设置如何。

在地面测量的常规点距下，约束不会随距离减弱：仅当两点间距超过参考距离（默认 50 m）时权重才开始衰减，距离更近时权重恰为 1。

设置文件中也可能包含 lateral_weight_scale。它是此值的乘数而非另一个控制项，因此有效权重为两者之积；它保持为 1.0，应修改的是此数值。</translation>
    </message>
    <message>
      <source>Pull log resistivity toward the starting reference model. Weight relative to vertical smoothness; default 0.4, zero disables it. With automatic start, the reference is chosen from the data. Applies to single soundings and line inversions; zero smoothness disables this term.</source>
      <translation>将对数电阻率拉向初始参考模型。权重相对于垂向光滑度而言；默认 0.4，设为零则禁用。使用自动初始模型时，参考模型由数据确定。适用于单点测深和测线反演；光滑度为零时此项也被禁用。</translation>
    </message>
    <message>
      <source>Smoothness</source>
      <translation>光滑度</translation>
    </message>
    <message>
      <source>Model damping</source>
      <translation>模型阻尼</translation>
    </message>
    <message>
      <source>Lateral smoothness</source>
      <translation>横向光滑度</translation>
    </message>
    <message>
      <source>Max iterations</source>
      <translation>最大迭代次数</translation>
    </message>
    <message>
      <source>DOI sensitivity</source>
      <translation>DOI 灵敏度</translation>
    </message>
    <message>
      <source>Data errors and calibration</source>
      <extracomment>Preset key to the control that carries it. Only settings the panel exposes appear; anything else in a preset reaches the run through :meth:`_collect_inv` reading the same defaults.</extracomment>
      <translation>数据误差与校准</translation>
    </message>
    <message>
      <source>Uncertainty applied to every gate alike: system calibration, and the error in representing the ground as 1D layers. Where the file carries a per-gate stack error, this is added in quadrature rather than replacing it, so a noisy gate stays noisy and a clean one takes this as its floor.

χ² is measured against the combined uncertainty, so this value is what "fitting the data" is measured against. A larger value makes the same model fit better; a smaller one makes it fit worse.</source>
      <translation>统一施加于每个时窗的不确定度：系统标定误差，以及将地下表示为一维层状模型的误差。若文件含有逐时窗的叠加误差，此值以平方和方式与之叠加而非替代，因此噪声大的时窗仍保持较大误差，干净的时窗则以此值为下限。

χ² 以合成不确定度为基准计算，因此此值就是衡量“拟合数据”的标准。值越大，同一模型的拟合越好；值越小，拟合越差。</translation>
    </message>
    <message>
      <source>Multiplies the observed data before inversion, for data in normalized units such as moment-normalized airborne dB/dt that carry a system calibration constant. 1.0 leaves the data unscaled.</source>
      <translation>反演前对观测数据乘以该系数，适用于带有系统标定常数的归一化单位数据，例如按磁矩归一化的航空 dB/dt。1.0 表示不缩放数据。</translation>
    </message>
    <message>
      <source>Auto-calibrate</source>
      <translation>自动标定</translation>
    </message>
    <message>
      <source>Estimates the amplitude scale from the shape of the decay. This keeps the inversion off the bounds; the absolute resistivity level it produces is approximate, since the shape alone does not fix it.</source>
      <translation>根据衰减曲线形态估算振幅比例。这可使反演避开边界约束；但仅凭形态无法确定绝对电阻率水平，因此所得结果为近似值。</translation>
    </message>
    <message>
      <source>Ties the amplitude scale to a half-space of this resistivity, in Ω·m, so the recovered model lands near this level. The data alone do not determine the absolute level, and the same value is applied the same way to every dataset.

0 turns this off. A non-zero value takes precedence over Auto-calibrate.</source>
      <translation>将振幅标度绑定到此电阻率（Ω·m）的半空间，使反演模型落在该水平附近。仅凭数据无法确定绝对水平，且同一数值以相同方式应用于每个数据集。

设为 0 则关闭。非零值优先于“自动标定”。</translation>
    </message>
    <message>
      <source>Smallest stack error a gate is allowed to claim. A gate that happens to stack quietly arrives at a few tenths of a percent, and on a station carrying four or five gates it then outweighs its neighbours by two orders of magnitude and drags the model onto itself.

A stack error is itself estimated from a finite number of repeats, so it scatters; floor it at the repeatability the instrument can actually resolve, typically a few percent. 0 turns the floor off and uses the recorded value.</source>
      <translation>时窗允许的最小叠加误差。恰好叠加得很安静的时窗，其误差可能只有零点几个百分点；在只有四五个时窗的测点上，它的权重会比相邻时窗高出两个数量级，把模型拉向自身。

叠加误差本身由有限次重复测量估计，存在离散；应将其下限设为仪器实际可分辨的重复性，通常为几个百分点。设为 0 则关闭下限，直接使用记录值。</translation>
    </message>
    <message>
      <source>Largest stack error used as an uncertainty. Capping a larger recorded error makes that noisy gate carry more weight than its file requests; it limits down-weighting and does not reject the gate.

0 turns the cap off. To remove noisy gates, use the stack-error cut on the loader panel instead.</source>
      <translation>用作不确定度的最大叠加误差。对更大的记录误差设上限会使该噪声时窗获得高于文件指定的权重；它只限制降权，不会剔除该时窗。

设为 0 则关闭上限。如需移除噪声时窗，请改用载入面板中的叠加误差剔除。</translation>
    </message>
    <message>
      <source>Lower bound on recovered resistivity, in Ω·m. The solver works in log10 resistivity and this is its box constraint.</source>
      <translation>反演电阻率的下限，单位 Ω·m。求解器在 log10 电阻率空间中计算，此值为其边界约束。</translation>
    </message>
    <message>
      <source>Upper bound on recovered resistivity, in Ω·m. A layer the data cannot resolve is driven only by the regularisation, so it walks until this bound stops it. Set it to the highest value the target geology can plausibly reach; a section whose deepest cells sit exactly on it is reporting the bound rather than the ground.</source>
      <translation>反演电阻率的上限（Ω·m）。数据无法分辨的层仅受正则化驱动，会一直变化直到被此上限挡住。请将其设为目标地质体可能达到的最高值；若断面最深处的单元恰好等于此值，反映的是上限而非实际地层。</translation>
    </message>
    <message>
      <source>Relative error</source>
      <translation>相对误差</translation>
    </message>
    <message>
      <source>Stack error bounds</source>
      <translation>叠加误差范围</translation>
    </message>
    <message>
      <source>Resistivity bounds</source>
      <translation>电阻率范围</translation>
    </message>
    <message>
      <source>Data scale / calib.</source>
      <translation>数据比例 / 校准</translation>
    </message>
    <message>
      <source>Reference ρ (Ω·m)</source>
      <translation>参考 ρ (Ω·m)</translation>
    </message>
    <message>
      <source>Line</source>
      <translation>测线</translation>
    </message>
    <message>
      <source>Uniform sounding spacing used for the section's x-axis when no geometry file is loaded.</source>
      <translation>未载入几何文件时，断面 x 轴所用的均匀测深间距。</translation>
    </message>
    <message>
      <source>all</source>
      <translation>全部</translation>
    </message>
    <message>
      <source>How many soundings to invert, counted from the first station of the survey (or of the chosen line). "all" inverts every one; a number is for a quick test, and the Run group says how many it leaves out. Stations are ordered by line, so a cap drops the last lines rather than thinning the survey.</source>
      <translation>要反演的测深数量，从测量（或所选测线）的第一个测点开始计数。"all" 反演全部测深；数值用于快速测试，“运行”组会显示排除了多少个。测点按测线排序，因此限制数量会舍弃最后几条测线，而不是对整个测量抽稀。</translation>
    </message>
    <message>
      <source>All lines</source>
      <translation>所有测线</translation>
    </message>
    <message>
      <source>Invert one survey line rather than the whole file. The lateral constraint never crosses a line, so a line run on its own is tied exactly as it would be in a full run; what changes is that it can carry its own gate selection and rejection settings, and that the other lines are not re-solved.

Use it where one line is noisier than the rest: run the good lines at the usual settings, then that line with a lower retention floor, and export each section separately.</source>
      <translation>反演单条测线而非整个文件。横向约束不会跨越测线，因此单独运行的测线与完整运行时的约束完全相同；不同之处在于它可以使用自己的时窗选择和剔除设置，且其他测线不会重新求解。

适用于某条测线噪声明显高于其他测线的情况：先按常规设置运行质量好的测线，再以较低的保留下限运行该测线，并分别导出各断面。</translation>
    </message>
    <message>
      <source>Simultaneous solves the whole line as one system, so the lateral constraint is enforced while each sounding is being fitted; it uses the analytic sensitivity, which makes it faster than inverting the soundings one at a time. Block-coordinate re-inverts one sounding at a time against its neighbours' models from the previous pass. Off inverts each sounding alone.</source>
      <translation>“同步”将整条测线作为一个系统求解，在拟合每个测深的同时施加横向约束；它使用解析灵敏度，因此比逐个反演测深更快。“块坐标”每次重新反演一个测深，并以相邻测深上一轮的模型为约束。“关闭”则单独反演每个测深。</translation>
    </message>
    <message>
      <source>Number of block-coordinate passes. The simultaneous solver does not use this setting.</source>
      <translation>块坐标迭代的遍数。同时求解器不使用此设置。</translation>
    </message>
    <message>
      <source>passes</source>
      <translation>遍数</translation>
    </message>
    <message>
      <source>TRF is the formal default: its trust-region step respects the resistivity bounds while solving. Gauss-Newton is retained for fast previews and exact reproduction of older project results.</source>
      <translation>TRF 是正式默认方法：其信赖域步长在求解时遵守电阻率边界。保留 Gauss-Newton 用于快速预览及精确复现旧工程结果。</translation>
    </message>
    <message>
      <source>Maximum forward evaluations in each fixed-error TRF stage. This is not the Gauss-Newton iteration count. Budget exhaustion is reported as incomplete and prevents error inflation.</source>
      <translation>每个固定误差 TRF 阶段的最大正演计算次数。这不是 Gauss-Newton 迭代次数。次数用尽将报告为未完成，并阻止误差放大。</translation>
    </message>
    <message>
      <source>TRF relative full-objective stopping tolerance. A tolerance far below the 1e-4 default can use up the evaluation budget before robust reweighting. The Ground TEM preset uses the looser 1e-3, which runs faster with nearly the same chi-squared.</source>
      <translation>TRF 全目标函数相对停止容差。远低于默认值 1e-4 的容差可能在稳健重加权之前就耗尽评估次数。地面 TEM 预设使用较宽松的 1e-3，运行更快，卡方几乎相同。</translation>
    </message>
    <message>
      <source>Threads used for the per-sounding forward and Jacobian. This machine reports {0} usable cores; auto takes one thread per sounding up to that number.

Each sounding owns its forward operator and the threads only read the shared model, so the models come back identical whatever this is set to. The work is NumPy underneath and releases the GIL for most of its duration, so scaling is real but short of linear.</source>
      <translation>用于逐测深正演和雅可比计算的线程数。本机报告有 {0} 个可用核心；auto 为每个测深分配一个线程，最多不超过该数目。

每个测深拥有自己的正演算子，线程只读取共享模型，因此无论此值如何设置，得到的模型都完全相同。底层计算基于 NumPy，大部分时间会释放 GIL，因此加速确实存在，但达不到线性。</translation>
    </message>
    <message>
      <source>Sounding spacing (m)</source>
      <translation>测深间距 (m)</translation>
    </message>
    <message>
      <source>Max soundings</source>
      <translation>最大测深数</translation>
    </message>
    <message>
      <source>Survey line</source>
      <translation>测线</translation>
    </message>
    <message>
      <source>Coupling</source>
      <translation>耦合</translation>
    </message>
    <message>
      <source>Solver</source>
      <translation>求解器</translation>
    </message>
    <message>
      <source>TRF max evaluations</source>
      <translation>TRF 最大评估次数</translation>
    </message>
    <message>
      <source>TRF ftol</source>
      <translation>TRF ftol</translation>
    </message>
    <message>
      <source>CPU threads</source>
      <translation>CPU 线程数</translation>
    </message>
    <message>
      <source>Fit assistance</source>
      <translation>拟合辅助</translation>
    </message>
    <message>
      <source>Auto-λ (re-solve for target χ²)</source>
      <translation>自动 λ（重新求解以达到目标 χ²）</translation>
    </message>
    <message>
      <source>The solve at the smoothness above always runs first and is always kept. If its χ² misses the target band, the line is re-solved with the vertical and lateral smoothness scaled together by a single factor (λ here), and the closest result is displayed. Each trial warm-starts from the nearest factor already solved. Applies to the simultaneous line solver.</source>
      <translation>始终先以上方的光滑度求解并保留其结果。若其 χ² 未落入目标范围，则以单一系数（此处为 λ）同时缩放垂向和横向光滑度，重新求解测线，并显示最接近目标的结果。每次试算都从已求解的最近系数热启动。适用于测线同步求解器。</translation>
    </message>
    <message>
      <source>χ² = 1 means the model explains the data to within the assumed relative error. The solve stops on reaching the band rather than fitting past it.</source>
      <translation>χ² = 1 表示模型在假定相对误差范围内解释了数据。求解到达该区间即停止，不会过度拟合。</translation>
    </message>
    <message>
      <source>Half-width of the accepted band. A step that would overshoot below it is shortened instead, so the reported χ² is not an accident of step length.</source>
      <translation>可接受区间的半宽。若某一步会越过其下限，则改为缩短步长，从而使报告的 χ² 不受步长偶然因素影响。</translation>
    </message>
    <message>
      <source>Target χ²</source>
      <translation>目标 χ²</translation>
    </message>
    <message>
      <source>Upper bound on the extra line solves the search may run, on top of the first one at the smoothness set above.</source>
      <translation>搜索可额外运行的测线求解次数上限（不含以上方设定光滑度进行的首次求解）。</translation>
    </message>
    <message>
      <source>Max trials</source>
      <translation>最大试算次数</translation>
    </message>
    <message>
      <source>Smallest factor the search may apply to the smoothness. Values well below 1 let it relax the model a long way to chase the target χ².</source>
      <translation>搜索可对光滑度施加的最小因子。远小于 1 的值允许大幅放松模型以逼近目标 χ²。</translation>
    </message>
    <message>
      <source>Largest factor the search may apply to the smoothness, used when the first solve fits better than the target and a stiffer model is wanted.</source>
      <translation>搜索可对光滑度施加的最大倍数，用于首次求解拟合优于目标值且需要更光滑模型的情况。</translation>
    </message>
    <message>
      <source>λ scale range</source>
      <translation>λ 缩放范围</translation>
    </message>
    <message>
      <source>Robust errors (keep all gates)</source>
      <translation>稳健误差（保留所有时窗）</translation>
    </message>
    <message>
      <source>Keep every imported gate. After an initial fit, Huber weights increase the effective error of large residuals without changing the recorded measurement error. A gate can regain weight on later passes. A large residual can also mean an inadequate model, not bad data. The quality report keeps original-error χ² separate from effective χ².</source>
      <translation>保留所有导入的时窗。初始拟合后，Huber 权重会增大大残差的有效误差，但不改变记录的测量误差。时窗可在后续轮次中恢复权重。大残差也可能意味着模型不充分，而非数据不良。质量报告将原始误差 χ² 与有效 χ² 分开列出。</translation>
    </message>
    <message>
      <source>Start downweighting when |prediction - data| / original error exceeds this threshold. With the target off, effective error = original error × sqrt(|residual| / cut). With a target, bounded inflation is calibrated on eligible gates only. Below the cut, errors are unchanged.</source>
      <translation>当 |prediction - data| / 原始误差 超过此阈值时开始降权。关闭目标时，有效误差 = 原始误差 × sqrt(|residual| / cut)。启用目标时，仅在符合条件的时窗上标定有界放大。低于阈值时，误差不变。</translation>
    </message>
    <message>
      <source>Maximum reweight-and-solve passes after the initial fit. Reuses the previous model and stops early if error factors are stable within 1%.</source>
      <translation>初始拟合后重加权并求解的最大轮数。沿用上一轮模型，若误差因子稳定在 1% 以内则提前停止。</translation>
    </message>
    <message>
      <source>Downweight beyond</source>
      <translation>超出则降权</translation>
    </message>
    <message>
      <source>Maximum effective/original error ratio. 10 limits the inverse-variance weight to at least 1/100 of its original value; it is never zero. Set to 1 to disable inflation without changing other settings.</source>
      <translation>有效误差与原始误差的最大比值。取 10 时，逆方差权重不低于原值的 1/100，且永不为零。设为 1 可在不改变其他设置的情况下禁用误差放大。</translation>
    </message>
    <message>
      <source>Max error factor</source>
      <translation>最大误差因子</translation>
    </message>
    <message>
      <source>Minimum fraction of gates whose effective error stays EXACTLY original on each pass. 0.70 protects at least 70%; only the worst remaining residuals above the sigma cut can be inflated. The protected identities may change. Applies to the whole simultaneous run, or each independent sounding.</source>
      <translation>每轮中有效误差严格保持原值的时窗最小比例。0.70 表示至少保护 70%；只有超过 sigma 截断值的剩余最差残差才会被放大。受保护的时窗可能变化。适用于整个同步运行，或每个独立测深。</translation>
    </message>
    <message>
      <source>Keep original errors (fraction)</source>
      <translation>保留原始误差（比例）</translation>
    </message>
    <message>
      <source>off (Huber only)</source>
      <translation>关（仅 Huber）</translation>
    </message>
    <message>
      <source>Optional EFFECTIVE chi2 target, reached by bounded error calibration on eligible gates and refitting. This is NOT independent evidence of fit quality. Original-error chi2 is still reported. 0 uses Huber-only weights.</source>
      <translation>可选的“有效” chi2 目标，通过对符合条件的时窗进行有界误差校准并重新拟合来达到。这并不能独立证明拟合质量。仍会报告基于原始误差的 chi2。0 表示仅使用 Huber 权重。</translation>
    </message>
    <message>
      <source>Effective χ² target</source>
      <translation>有效 χ² 目标值</translation>
    </message>
    <message>
      <source>Advanced: empirical resistive-background prior</source>
      <translation>高级：经验高阻背景先验</translation>
    </message>
    <message>
      <source>Enable empirical background tendency</source>
      <translation>启用经验背景趋势</translation>
    </message>
    <message>
      <source>A sustained weak absolute LM response can be consistent with a resistive background, but it cannot locate that resistivity in a shallow layer. This adds a weak one-sided tendency across the whole 1-D model. It is an empirical assumption, not independent geology, and is excluded from data chi2 and sensitivity/DOI evidence.</source>
      <translation>持续较弱的 LM 绝对响应可能与高阻背景相符，但无法将该电阻率定位到某一浅层。此项在整个一维模型上施加较弱的单侧倾向。这是经验假设，并非独立的地质信息，且不计入数据 chi2 及灵敏度/DOI 依据。</translation>
    </message>
    <message>
      <source>Weak absolute LM signal</source>
      <translation>低磁矩绝对信号弱</translation>
    </message>
    <message>
      <source>Declining LM quality</source>
      <translation>LM 质量下降</translation>
    </message>
    <message>
      <source>Manual (all selected stations)</source>
      <translation>手动（所有选中测点）</translation>
    </message>
    <message>
      <source>Auto (instrument forward)</source>
      <translation>自动（仪器正演）</translation>
    </message>
    <message>
      <source>Raw project-response units, BEFORE inversion data_scale. 0 computes the LM response of a fixed 1000 Ω·m homogeneous reference half-space, using each station's actual waveform, filters, gate and geometry. A positive value overrides that limit; e.g. 3e-9 for a raw LM gate near 8.95 µs. The fixed trigger reference is deliberately separate from the soft model target. 80% of a full rolling window must lie below the limit; missing gates do not count.</source>
      <translation>原始工程响应单位，在反演 data_scale 之前。0 表示使用每个测点的实际波形、滤波器、时窗和几何参数，计算固定 1000 Ω·m 均匀参考半空间的 LM 响应。正值会覆盖该限值；例如对于约 8.95 µs 的原始 LM 时窗可设为 3e-9。固定触发参考有意与软模型目标分开。完整滚动窗口中须有 80% 低于该限值；缺失的时窗不计入。</translation>
    </message>
    <message>
      <source>Prior trigger</source>
      <translation>前次触发</translation>
    </message>
    <message>
      <source>LM signal threshold</source>
      <translation>LM 信号阈值</translation>
    </message>
    <message>
      <source>Automatic one-sided target divided by the effective starting half-space. 2 is deliberately modest: it expresses a resistive tendency without forcing an order-of-magnitude jump. The target is capped at rho_max. When auto-start is active, this uses the half-space selected from the data.</source>
      <translation>自动单侧目标值与有效初始半空间之比。2 是刻意保守的取值：表达高阻倾向而不强制产生数量级的跃变。目标值上限为 rho_max。启用自动初始值时，使用由数据选定的半空间。</translation>
    </message>
    <message>
      <source>Residual multiplier; squared in the penalty. 0 disables its influence.</source>
      <translation>残差乘数；在罚项中取平方。设为 0 则不产生影响。</translation>
    </message>
    <message>
      <source>Activate below this fraction of the first window's median early LM SNR.</source>
      <translation>当低于首个窗口早期 LM 信噪比中位数的该比例时启用。</translation>
    </message>
    <message>
      <source>Target / initial model</source>
      <translation>目标 / 初始模型</translation>
    </message>
    <message>
      <source>Prior strength</source>
      <translation>先验强度</translation>
    </message>
    <message>
      <source>Quality window (stations)</source>
      <translation>质量窗口（测点数）</translation>
    </message>
    <message>
      <source>SNR / initial SNR trigger</source>
      <translation>SNR / 初始 SNR 触发阈值</translation>
    </message>
    <message>
      <source>Run</source>
      <translation>运行</translation>
    </message>
    <message>
      <source>Run inversion</source>
      <translation>运行反演</translation>
    </message>
    <message>
      <source>Backend</source>
      <translation>后端</translation>
    </message>
    <message>
      <source>Export recovered model (csv)…</source>
      <translation>导出反演模型 (csv)…</translation>
    </message>
    <message>
      <source>After a line inversion: model_cells.csv, one row per layer per sounding with its map coordinate, elevation, resistivity, sensitivity and χ², plus soundings.csv, one row per station. After a single sounding: the recovered model as npy and csv.

Both are written next to the section automatically. This writes a second copy to a chosen folder.</source>
      <translation>测线反演后：model_cells.csv，每个测深的每一层一行，包含地图坐标、高程、电阻率、灵敏度和 χ²；另有 soundings.csv，每个测点一行。单点测深反演后：以 npy 和 csv 保存反演模型。

两者都会自动写入断面所在位置。此操作会将副本另存到所选文件夹。</translation>
    </message>
    <message>
      <source>Raw tTEM SKB files do not contain TEM2Go inversion flags.</source>
      <translation>原始 tTEM SKB 文件不包含 TEM2Go 反演标记。</translation>
    </message>
    <message>
      <source>Use the enabled-gate flags stored by the TEM2Go project.</source>
      <translation>使用 TEM2Go 工程中保存的时窗启用标记。</translation>
    </message>
    <message>
      <source>Raw tTEM geometry is editable below. Manual defaults are only a fallback until the instrument-specific GEX/TFI files are supplied.</source>
      <translation>可在下方编辑原始 tTEM 几何参数。手动默认值仅在提供仪器专用 GEX/TFI 文件之前作为后备。</translation>
    </message>
    <message>
      <source>Select tTEM {0}</source>
      <translation>选择 tTEM {0}</translation>
    </message>
    <message>
      <source>Checking SimPEG backend… You can keep using the studio.</source>
      <translation>正在检查 SimPEG 后端… 可继续使用 Studio。</translation>
    </message>
    <message>
      <source>Ready: SimPEG backend available.</source>
      <translation>就绪：SimPEG 后端可用。</translation>
    </message>
    <message>
      <source>Unavailable: check the geophysics extra (SimPEG + discretize). {0}</source>
      <translation>不可用：请检查 geophysics 扩展依赖（SimPEG + discretize）。{0}</translation>
    </message>
    <message>
      <source>Select TEMcompany project</source>
      <translation>选择 TEMcompany 工程</translation>
    </message>
    <message>
      <source>{0} holds {1} projects:</source>
      <translation>{0} 包含 {1} 个工程：</translation>
    </message>
    <message>
      <source>Load EM project folder</source>
      <translation>载入 EM 工程文件夹</translation>
    </message>
    <message>
      <source>Load EM data</source>
      <translation>载入 EM 数据</translation>
    </message>
    <message>
      <source>Example: {0}</source>
      <translation>示例：{0}</translation>
    </message>
    <message>
      <source>Load failed: {0}</source>
      <translation>载入失败：{0}</translation>
    </message>
    <message>
      <source>{0}&lt;br&gt;{1} enabled channels ({2}{3}, {4}){5}</source>
      <translation>{0}&lt;br&gt;{1} 个启用通道（{2}{3}，{4}）{5}</translation>
    </message>
    <message>
      <source>Geometry (TEMcompany): {0} soundings, {1:.1f} m path, {2}{3}.</source>
      <translation>几何 (TEMcompany)：{0} 个测深，路径 {1:.1f} m，{2}{3}。</translation>
    </message>
    <message>
      <source>Applied {0} and {1}. Geometry, waveform, gates, import FIR, and the GEX analog response are active in both the SimPEG forward response and Jacobian (receiver 2-pole {2:g} kHz; TiB {3}-pole {4:g} kHz).</source>
      <translation>已应用 {0} 和 {1}。几何、波形、时窗、导入 FIR 以及 GEX 模拟响应均已在 SimPEG 正演响应和雅可比矩阵中生效（接收 2 极点 {2:g} kHz；TiB {3} 极点 {4:g} kHz）。</translation>
    </message>
    <message>
      <source>Applied {0} and {1}, but the GEX has no supported RxCoilLPFilter/TiBLowPassFilter definition.</source>
      <translation>已应用 {0} 和 {1}，但该 GEX 没有受支持的 RxCoilLPFilter/TiBLowPassFilter 定义。</translation>
    </message>
    <message>
      <source>Missing {0}. Area, Tx–Rx separation and height below are active, but full instrument calibration is incomplete.</source>
      <translation>缺少 {0}。下方的面积、Tx–Rx 间距和高度已生效，但完整的仪器标定尚不完整。</translation>
    </message>
    <message>
      <source>Geometry (auto): {0}, {1} soundings{2}.</source>
      <translation>几何（自动）：{0}，{1} 个测深{2}。</translation>
    </message>
    <message>
      <source>Load line geometry</source>
      <translation>载入测线几何</translation>
    </message>
    <message>
      <source>Geometry: {0} soundings, {1:.0f} m span{2}.</source>
      <extracomment>What ``get_acquisition`` can be asked for, and where each lives in what the reader returns.</extracomment>
      <translation>几何：{0} 个测深，跨度 {1:.0f} m{2}。</translation>
    </message>
    <message>
      <source>Inverting…</source>
      <translation>正在反演…</translation>
    </message>
    <message>
      <source>Resistivity (Ω·m)</source>
      <translation>电阻率 (Ω·m)</translation>
    </message>
    <message>
      <source>Recovered model</source>
      <translation>反演模型</translation>
    </message>
    <message>
      <source>Frequency (Hz)</source>
      <translation>频率 (Hz)</translation>
    </message>
    <message>
      <source>Time (s)</source>
      <translation>时间 (s)</translation>
    </message>
    <message>
      <source>Data fit (chi2={0:.2f})</source>
      <translation>数据拟合 (chi2={0:.2f})</translation>
    </message>
    <message>
      <source>Export recovered model to folder</source>
      <translation>导出反演模型到文件夹</translation>
    </message>
    <message>
      <source>EM sounding input format</source>
      <translation>EM 测深输入格式</translation>
    </message>
    <message>
      <source>Close</source>
      <translation>关闭</translation>
    </message>
    <message>
      <source>Apparent resistivity (Ω·m)</source>
      <translation>视电阻率（Ω·m）</translation>
    </message>
    <message>
      <source>Time step:</source>
      <translation>时间步：</translation>
    </message>
    <message>
      <source>Which time-lapse inversion result is displayed.</source>
      <translation>显示哪一个时移反演结果。</translation>
    </message>
    <message>
      <source>Previous time step</source>
      <translation>上一时间步</translation>
    </message>
    <message>
      <source>Next time step</source>
      <translation>下一时间步</translation>
    </message>
    <message>
      <source>Show:</source>
      <translation>显示：</translation>
    </message>
    <message>
      <source>Resistivity</source>
      <translation>电阻率</translation>
    </message>
    <message>
      <source>Resistivity shows the inverted model. “% change from baseline” shows 100 × (ρ − ρ₀) / ρ₀ against the first time step, on a diverging scale centred on zero.</source>
      <translation>“电阻率”显示反演模型。“相对基准的变化 %”显示相对于第一个时间步的 100 × (ρ − ρ₀) / ρ₀，采用以零为中心的发散色标。</translation>
    </message>
    <message>
      <source>Model:</source>
      <translation>模型：</translation>
    </message>
    <message>
      <source>The auto-λ search re-inverted at a different λ. Selects between that model and the one at the λ set above.</source>
      <translation>自动 λ 搜索以不同的 λ 重新反演。在该模型与上方设定 λ 下的模型之间进行选择。</translation>
    </message>
    <message>
      <source>Open 3D model</source>
      <translation>打开三维模型</translation>
    </message>
    <message>
      <source>The inversion ran on a 3D mesh; this section is the model along the line. Open the whole 3D model in the 3D viewer.</source>
      <translation>反演在三维网格上运行；此断面为沿测线的模型。可在三维查看器中打开完整三维模型。</translation>
    </message>
    <message>
      <source>Data</source>
      <translation>数据</translation>
    </message>
    <message>
      <source>Reciprocal errors</source>
      <translation>互易误差</translation>
    </message>
    <message>
      <source>Mesh</source>
      <translation>网格</translation>
    </message>
    <message>
      <source>Load resistivity data</source>
      <translation>载入电阻率数据</translation>
    </message>
    <message>
      <source>One survey</source>
      <translation>单次勘探</translation>
    </message>
    <message>
      <source>Invert the survey selected in the list - the one on the Data tab.</source>
      <translation>反演列表中所选的测量，即数据选项卡中的测量。</translation>
    </message>
    <message>
      <source>Time-lapse series</source>
      <translation>时移序列</translation>
    </message>
    <message>
      <source>Invert every survey in the list together, in list order: the first is the baseline, and each later one is compared with the one before it. The time-lapse options appear below the inversion settings.</source>
      <translation>按列表顺序联合反演列表中的所有测量：第一个为基准，其后每个与前一个进行比较。时移选项显示在反演设置下方。</translation>
    </message>
    <message>
      <source>Invert as</source>
      <translation>反演方式</translation>
    </message>
    <message>
      <source>Instrument / format</source>
      <translation>仪器 / 格式</translation>
    </message>
    <message>
      <source>Click a row to preview it. Each file is one time step; the list runs from earliest at the top to latest at the bottom. Use Sort by time to order the sequence.</source>
      <translation>点击某行以预览。每个文件为一个时间步；列表自上而下由早到晚排列。使用“按时间排序”整理序列。</translation>
    </message>
    <message>
      <source>Add files…</source>
      <translation>添加文件…</translation>
    </message>
    <message>
      <source>Add one or more ERT files, one per survey for time-lapse. Choose the instrument / format first.</source>
      <translation>添加一个或多个 ERT 文件，时移测量每次测量一个文件。请先选择仪器/格式。</translation>
    </message>
    <message>
      <source>Move selected up</source>
      <translation>上移所选项</translation>
    </message>
    <message>
      <source>Move selected down</source>
      <translation>下移所选项</translation>
    </message>
    <message>
      <source>Sort by time</source>
      <translation>按时间排序</translation>
    </message>
    <message>
      <source>Put the files in acquisition order, using the times read from their names or headers. A time-lapse inversion compares each survey with the one before it, so the order is part of the result.</source>
      <translation>依据从文件名或文件头读取的时间，按采集顺序排列文件。时移反演会将每次勘探与前一次进行比较，因此顺序也是结果的一部分。</translation>
    </message>
    <message>
      <source>Clear</source>
      <translation>清除</translation>
    </message>
    <message>
      <source>No files added.</source>
      <translation>未添加文件。</translation>
    </message>
    <message>
      <source>Date undated files by when they were last saved</source>
      <translation>按最后保存时间为无日期文件确定日期</translation>
    </message>
    <message>
      <source>Use each file's last-modified time as its acquisition time when neither its name nor its header gives one. Off by default: a file that was copied or re-exported carries the time of the copy, not of the survey.</source>
      <translation>当文件名和文件头均未提供采集时间时，以文件的最后修改时间作为采集时间。默认关闭：复制或重新导出的文件带有的是复制时间，而非测量时间。</translation>
    </message>
    <message>
      <source>Pair reciprocal files with their forward file</source>
      <translation>将互易文件与其正向文件配对</translation>
    </message>
    <message>
      <source>Some instruments write each survey as two files: the forward readings, and a few minutes later the reciprocal readings (“recip” in the name). Ticked, each reciprocal file is joined to the forward file measured just before it with the same name, and the two are one survey: one row in the list, at the forward file's time, one time step, and the readings of both in one data set, so each reading can be compared with its reciprocal.

A forward file with no reciprocal stays a survey on its own. A reciprocal file with no forward file is left out, and the line above names it.

Untick it if a file was joined to the wrong partner: every file is then a survey of its own again.</source>
      <translation>部分仪器将每次测量写为两个文件：正向读数，以及几分钟后的互易读数（文件名中含“recip”）。勾选后，每个互易文件会与紧接其前测得的同名正向文件合并为一次测量：在列表中占一行，采用正向文件的时间，作为一个时间步，两者的读数合并为一个数据集，以便将每个读数与其互易读数比较。

没有互易文件的正向文件仍单独作为一次测量。没有正向文件的互易文件会被排除，并在上方一行中列出其名称。

如有文件与错误的文件合并，请取消勾选：此时每个文件都重新单独作为一次测量。</translation>
    </message>
    <message>
      <source>Electrode file (optional)…</source>
      <translation>电极文件（可选）…</translation>
    </message>
    <message>
      <source>The file formats this page reads, the electrode file, and how to give each survey its time.</source>
      <translation>本页可读取的文件格式、电极文件，以及如何为每次测量指定时间。</translation>
    </message>
    <message>
      <source>No data loaded.</source>
      <translation>未载入数据。</translation>
    </message>
    <message>
      <source>Data QC / filter</source>
      <translation>数据 QC / 滤波</translation>
    </message>
    <message>
      <source>Average each reading with its reciprocal</source>
      <translation>将每个读数与其互易读数取平均</translation>
    </message>
    <message>
      <source>Load ERT data first.</source>
      <translation>请先载入 ERT 数据。</translation>
    </message>
    <message>
      <source>Drop measurements with relative error above this (0 = off). 20 % drops the readings a file's own error column calls noisy; a file with none of its own carries the 5 % assumed for every reading, and loses nothing.</source>
      <translation>剔除相对误差高于此值的测量（0 = 关闭）。20 % 会剔除文件自身误差列标记为噪声的读数；没有误差列的文件对每个读数均假定 5 %，不会剔除任何数据。</translation>
    </message>
    <message>
      <source>Min ρa</source>
      <translation>最小 ρa</translation>
    </message>
    <message>
      <source>Max ρa</source>
      <translation>最大 ρa</translation>
    </message>
    <message>
      <source>Max error</source>
      <translation>最大误差</translation>
    </message>
    <message>
      <source>More checks</source>
      <translation>更多检查</translation>
    </message>
    <message>
      <source>Extra QC criteria. They stay folded because most surveys need none of them, and the ones a given file cannot support are disabled with the reason in their tooltip.</source>
      <translation>附加 QC 标准。大多数测量无需使用，因此默认折叠；当前文件不支持的标准将被禁用，原因见其工具提示。</translation>
    </message>
    <message>
      <source>Drop ρa ≤ 0</source>
      <translation>剔除 ρa ≤ 0</translation>
    </message>
    <message>
      <source>A non-positive apparent resistivity is a polarity or geometry error rather than a measurement, and the inversion cannot use it. On with More checks. Min ρa above already removes negatives once it is set above zero.</source>
      <translation>非正的视电阻率是极性或几何错误，而非测量值，反演无法使用。在“更多检查”中启用。上方的最小 ρa 一旦设为大于零，即已剔除负值。</translation>
    </message>
    <message>
      <source>Min |V|</source>
      <translation>最小 |V|</translation>
    </message>
    <message>
      <source>Min |I|</source>
      <translation>最小 |I|</translation>
    </message>
    <message>
      <source>Drop configurations whose geometric factor exceeds this (0 = off). A large |k| multiplies the measured resistance, and its noise with it, which is how a clean-looking rhoa outlier is produced by geometry rather than by ground. Set from the file once one is loaded.</source>
      <translation>剔除几何因子超过此值的装置（0 = 关闭）。较大的 |k| 会放大实测电阻及其噪声，这正是看似正常的 rhoa 离群值由几何而非地层造成的原因。载入文件后将根据文件设置。</translation>
    </message>
    <message>
      <source>Max |k|</source>
      <translation>最大 |k|</translation>
    </message>
    <message>
      <source>Max contact R</source>
      <translation>最大接地电阻</translation>
    </message>
    <message>
      <source>Drop readings whose potential scattered by more than this across its own samples, as a percentage of the potential (0 = off). Subsurface Insights records it. A few percent is normal; hundreds of percent is an electrode or a contact failing.</source>
      <translation>剔除电位在其自身采样间离散程度超过此值（以电位的百分比计）的读数（0 = 关闭）。Subsurface Insights 会记录该值。几个百分点属正常；数百个百分点则表明电极或接地故障。</translation>
    </message>
    <message>
      <source>Max stacking spread</source>
      <translation>最大叠加离散度</translation>
    </message>
    <message>
      <source>Max recip. error</source>
      <translation>最大互易误差</translation>
    </message>
    <message>
      <source>Load data to see which checks are available.</source>
      <translation>载入数据以查看可用的检查项。</translation>
    </message>
    <message>
      <source>Apply filter</source>
      <translation>应用滤波</translation>
    </message>
    <message>
      <source>Reset</source>
      <translation>重置</translation>
    </message>
    <message>
      <source>Quick runs the inversion and nothing else, which is the shorter run while λ and the mesh are still being settled.

Thorough adds the two stages Quick drops. It checks the geometric factors (k) against the mesh, repairing them when they disagree, and it searches λ for the target χ².

The k check is the one with the most evidence behind it: a wrong k scales the whole section by a constant and χ² never notices, so a Quick result that looks perfect can still be uniformly wrong. Re-run Thorough whenever the resistivities themselves look off, not only when the fit looks bad.</source>
      <translation>“快速”仅运行反演，不做其他处理，在 λ 和网格仍在调整时运行时间更短。

“全面”会加入“快速”省略的两个阶段：根据网格检查几何因子 (k)，在不一致时进行修复；并搜索达到目标 χ² 的 λ。

k 检查是依据最充分的一项：错误的 k 会使整个断面按常数缩放，而 χ² 无法察觉，因此看似完美的“快速”结果仍可能整体偏差。只要电阻率本身看起来不对，就应重新运行“全面”，而不仅限于拟合效果差的时候。</translation>
    </message>
    <message>
      <source>Mode</source>
      <translation>模式</translation>
    </message>
    <message>
      <source>Solver. The in-house Gauss-Newton inversion exposes its own stopping rule and line search, so the fit assistance below drives it directly. The PyGIMLi manager runs its own loop and is available as a cross-check.

ADTLERT uses a CUDA-accelerated cuDSS forward solve and GPU CGLS: 2.5D on a profile, 3D on an imported tetrahedral mesh. A CUDA 12 GPU is required; cuDSS and NVRTC come with ADTLERT. Windows is supported; Linux is recommended for the best performance. Pole arrays (remote electrodes) run too. The controls below remain available when this engine is selected.

E4D is PNNL's parallel 3D code, run as an external program under MPI; it is not installed with PyHydroGeophysX. It runs on Linux, on Windows only inside WSL 2, and on macOS when built from source. A profile is inverted in 3D on a mesh built around the line and shown as the section along it. A time-lapse series runs as E4D's own time-lapse inversion: the first survey is the baseline, and each later one starts from the solution before it, with the change from it smoothed.

R2 (2D profiles) and R3t (3D surveys, or a profile on a 3D mesh around the line) are Andrew Binley's codes, the ones ResIPy runs; they are found in an installed ResIPy unless named below. They are Windows programs: native on Windows, through Wine on Linux and macOS, free for non-commercial use. Both choose their own smoothing weight at every iteration, so λ and auto-λ do not apply; they hold fixed zones fixed. A time-lapse series is their difference inversion against the first survey.</source>
      <translation>求解器。内置 Gauss-Newton 反演提供自己的停止准则和线搜索，因此下方的拟合辅助可直接驱动它。PyGIMLi 管理器运行自己的迭代循环，可用作交叉检验。

ADTLERT 使用 CUDA 加速的 cuDSS 正演求解和 GPU CGLS：剖面上为 2.5D，导入的四面体网格上为 3D。需要支持 CUDA 12 的 GPU；cuDSS 和 NVRTC 随 ADTLERT 提供。支持 Windows；为获得最佳性能推荐使用 Linux。也支持单极装置（远电极）。选择此引擎时，下方控件仍可使用。

E4D 是 PNNL 的并行三维程序，作为外部程序在 MPI 下运行；它不随 PyHydroGeophysX 安装。它可在 Linux 上运行，在 Windows 上仅能在 WSL 2 中运行，在 macOS 上需从源码编译。剖面在围绕测线构建的网格上进行三维反演，并显示为沿测线的断面。时移序列采用 E4D 自身的时移反演：第一次测量为基准，之后每次测量都从前一个解开始，并对相对其的变化进行平滑。

R2（二维剖面）和 R3t（三维测量，或在围绕测线的三维网格上的剖面）是 Andrew Binley 的程序，即 ResIPy 所调用的程序；除非在下方指定，否则从已安装的 ResIPy 中查找。它们是 Windows 程序：在 Windows 上原生运行，在 Linux 和 macOS 上通过 Wine 运行，非商业用途免费。两者在每次迭代中自行选择平滑权重，因此 λ 和自动 λ 不适用；固定分区保持固定。时移序列采用相对第一次测量的差分反演。</translation>
    </message>
    <message>
      <source>Engine</source>
      <translation>引擎</translation>
    </message>
    <message>
      <source>Spatial regularization strength (smoothness). Lower fits the data harder, higher gives a smoother model. Start on the smooth side: the auto-λ search relaxes downward, continuing each λ from the previous solution, and that direction is the stable one. Values below 1 are allowed; the range is {0:g} to {1:g} and the arrows step by one significant digit.</source>
      <translation>空间正则化强度（光滑度）。值越低对数据拟合越紧，值越高模型越光滑。建议从较光滑一侧开始：自动 λ 搜索向下放松，每个 λ 都从上一个解继续，这一方向更稳定。允许小于 1 的值；范围为 {0:g} 至 {1:g}，箭头按一位有效数字步进。</translation>
    </message>
    <message>
      <source>Lambda</source>
      <translation>正则化系数 λ</translation>
    </message>
    <message>
      <source>The most iterations the inversion may take (for each λ when Auto-λ is on). It normally stops sooner, once χ² stops improving (next row). Reaching this limit means the fit could still improve, and the log says so.</source>
      <translation>反演允许的最大迭代次数（启用自动 λ 时为每个 λ 的次数）。通常在 χ² 不再改善时（见下一行）提前停止。达到此上限意味着拟合仍有改进空间，日志中会注明。</translation>
    </message>
    <message>
      <source>The most iterations of the time-lapse inversion; with Windowed on, of each window.</source>
      <translation>时移反演的最大迭代次数；启用“分窗”时为每个窗口的最大迭代次数。</translation>
    </message>
    <message>
      <source>Stop when χ² improves</source>
      <translation>χ² 改善时停止</translation>
    </message>
    <message>
      <source>The mesh, its sizing and what the a-priori zones do to it are set on the Mesh tab, which draws the mesh the run will invert on.</source>
      <translation>网格、其尺寸以及先验分区对网格的作用均在“网格”标签页中设置，该页会绘制本次运行将用于反演的网格。</translation>
    </message>
    <message>
      <source>Data errors</source>
      <translation>数据误差</translation>
    </message>
    <message>
      <source>Where the per-measurement error comes from. Most instruments write an err column; replacing it with an assumed percentage makes χ² report on an error model the data never had. The stacking spread is offered for data that record it, the reciprocal error model for data measured both ways.</source>
      <translation>每个测量误差的来源。多数仪器会写出 err 列；若以假定百分比替代，χ² 反映的将是数据本不具备的误差模型。对记录了叠加离散度的数据提供叠加离散度，对正反向均测量的数据提供互易误差模型。</translation>
    </message>
    <message>
      <source>Taken from</source>
      <translation>取自</translation>
    </message>
    <message>
      <source>Assumed relative data error, used when estimating and as the fallback where the file has no usable value.</source>
      <translation>假定的相对数据误差，用于估算，并在文件中无可用值时作为备用。</translation>
    </message>
    <message>
      <source>Absolute resistance error, added as absolute/|R|. It raises the error bar on weak readings, which is where a flat percentage is most optimistic. Leave at 0 when the survey spans a narrow signal range.</source>
      <translation>绝对电阻误差，以 absolute/|R| 形式叠加。它会增大弱读数的误差棒，而这正是固定百分比误差最乐观的地方。若测量信号范围较窄，保持为 0。</translation>
    </message>
    <message>
      <source>Estimate</source>
      <translation>估算</translation>
    </message>
    <message>
      <source>No reading is given a smaller error than this when its error comes from reciprocals: the error model, or an averaged pair's own difference. Two directions that agree closely still share the errors that cannot differ between them - the electrode positions, the 2-D assumption - so a near-perfect pair is not an error-free reading. 1 % is also the smallest error the in-house and ADTLERT time-lapse inversions accept. Averaged pairs take it when Apply filter averages them; the model takes it when the inversion runs.</source>
      <translation>当读数的误差来自互易测量（误差模型或平均配对自身的差值）时，任何读数的误差都不会小于此值。两个方向即使高度一致，仍共享二者之间无法产生差异的误差——电极位置、二维假设——因此近乎完美的配对并非无误差读数。1 % 也是内部时移反演和 ADTLERT 时移反演所接受的最小误差。“应用滤波”对配对取平均时，平均后的配对采用此值；运行反演时，误差模型采用此值。</translation>
    </message>
    <message>
      <source>Minimum</source>
      <translation>最小值</translation>
    </message>
    <message>
      <source>Auto-λ: re-invert to reach target χ²</source>
      <translation>自动 λ：重新反演以达到目标 χ²</translation>
    </message>
    <message>
      <source>The inversion at the λ above always runs first and is always kept. If its χ² misses the target band, the same mesh is re-inverted at other λ values (bracket, then bisect in log λ) and the closest one becomes the displayed model. Each trial continues from the nearest λ already solved rather than restarting, so the later ones are cheap, but every trial is still a full inversion.</source>
      <translation>始终先以上方的 λ 运行反演并保留其结果。若其 χ² 未落入目标范围，则在同一网格上以其他 λ 值重新反演（先确定区间，再在 log λ 上二分），并显示最接近目标的模型。每次试算都从已求解的最近 λ 继续，而非重新开始，因此后续试算开销较小，但每次试算仍是一次完整反演。</translation>
    </message>
    <message>
      <source>χ² = 1 means the model explains the data to within the assumed relative error. A larger target accepts a looser fit, matching data noisier than the error estimate describes.</source>
      <translation>χ² = 1 表示模型在假定相对误差范围内解释了数据。目标值越大，接受的拟合越宽松，适用于噪声大于误差估计的数据。</translation>
    </message>
    <message>
      <source>Half-width of the accepted band. The search stops as soon as a trial lands inside target ± tolerance.</source>
      <translation>可接受区间的半宽。一旦某次试算落入目标值 ± 容差范围内，搜索即停止。</translation>
    </message>
    <message>
      <source>Upper bound on the extra inversions the λ search may run, on top of the first one at the λ set above. Reached only when the target stays out of range.</source>
      <translation>λ 搜索可额外运行的反演次数上限（不含以上方设定 λ 进行的首次反演）。仅当目标始终未达到时才会用满。</translation>
    </message>
    <message>
      <source>Max λ trials</source>
      <translation>最大 λ 试算次数</translation>
    </message>
    <message>
      <source>Reject outliers: drop data the model cannot explain</source>
      <translation>剔除异常值：舍弃模型无法解释的数据</translation>
    </message>
    <message>
      <source>After the inversion converges, the measurements whose residual exceeds the threshold below are dropped and the inversion runs again. This addresses a high χ² caused by individual bad readings rather than by the model.

It also shrinks the dataset; the floor below bounds how much can be removed.</source>
      <translation>反演收敛后，残差超过下方阈值的测量数据将被剔除，并重新运行反演。这用于处理由个别坏读数而非模型引起的高 χ²。

这也会缩减数据集；下方的下限限制了可剔除的数量。</translation>
    </message>
    <message>
      <source>Rejection cut in units of the assumed error. A datum at 3 means the model misses it by three times its own error bar.</source>
      <translation>以假定误差为单位的剔除阈值。某数据为 3 表示模型与其偏差为其自身误差棒的三倍。</translation>
    </message>
    <message>
      <source>How many reject-and-re-invert cycles to run. Each pass is a full inversion.</source>
      <translation>剔除并重新反演的循环次数。每一轮均为一次完整反演。</translation>
    </message>
    <message>
      <source>σ, passes</source>
      <translation>σ，遍数</translation>
    </message>
    <message>
      <source>Cut beyond</source>
      <translation>超出即截断</translation>
    </message>
    <message>
      <source>Rejection stops before it would leave less than this share of the measurements. A χ² bought by deleting most of the survey is not a fit.</source>
      <translation>若继续剔除会使剩余测量数据少于此比例，则停止剔除。通过删除大部分勘探数据换来的 χ² 并不是真正的拟合。</translation>
    </message>
    <message>
      <source>Keep at least</source>
      <translation>至少保留</translation>
    </message>
    <message>
      <source>Export resistivity model…</source>
      <translation>导出电阻率模型…</translation>
    </message>
    <message>
      <source>Export the inverted model as npy + pygimli mesh (.bms) + VTK.</source>
      <translation>将反演模型导出为 npy + pygimli 网格 (.bms) + VTK。</translation>
    </message>
    <message>
      <source>Export time-lapse results…</source>
      <translation>导出时移结果…</translation>
    </message>
    <message>
      <source>Saves the time-lapse models to a chosen folder: a combined VTK, per-step VTKs, final_models.npy, the mesh (.bms), times CSV, and the figure.</source>
      <translation>将时移模型保存到所选文件夹：合并 VTK、各时间步 VTK、final_models.npy、网格 (.bms)、时间 CSV 以及图件。</translation>
    </message>
    <message>
      <source>Open output folder</source>
      <translation>打开输出文件夹</translation>
    </message>
    <message>
      <source>Export model</source>
      <translation>导出模型</translation>
    </message>
    <message>
      <source>Run time-lapse inversion</source>
      <translation>运行时移反演</translation>
    </message>
    <message>
      <source>Time-lapse</source>
      <translation>时移</translation>
    </message>
    <message>
      <source>Temporal regularization strength (couples consecutive time steps).</source>
      <translation>时间正则化强度（耦合相邻时间步）。</translation>
    </message>
    <message>
      <source>Alpha (temporal)</source>
      <translation>Alpha（时间）</translation>
    </message>
    <message>
      <source>Temporal norm: L2 smooth, L1 blocky, L1L2 hybrid.</source>
      <translation>时间范数：L2 为光滑，L1 为块状，L1L2 为混合。</translation>
    </message>
    <message>
      <source>Norm</source>
      <translation>范数</translation>
    </message>
    <message>
      <source>Weight by the interval between surveys</source>
      <translation>按测量间隔加权</translation>
    </message>
    <message>
      <source>Penalize the rate of change rather than the raw difference, so a month-long gap is allowed proportionally more change than an hour-long one. Weights are normalized by the median interval, so an evenly sampled series is unchanged and Alpha keeps its meaning. Untick to constrain every pair equally.</source>
      <translation>惩罚变化速率而非原始差值，因此相隔一个月的间隔所允许的变化按比例大于相隔一小时的间隔。权重按中位间隔归一化，因此等间隔采样的序列不受影响，Alpha 的含义保持不变。取消勾选则对每一对施加相同的约束。</translation>
    </message>
    <message>
      <source>Windowed (sliding window)</source>
      <translation>加窗（滑动窗口）</translation>
    </message>
    <message>
      <source>Process consecutive time steps in overlapping windows: cheaper and lower-memory for long monitoring sequences.</source>
      <translation>以重叠窗口处理连续的时间步：对长期监测序列而言计算量更小、内存占用更低。</translation>
    </message>
    <message>
      <source>Window size</source>
      <translation>窗口大小</translation>
    </message>
    <message>
      <source>Low memory (sparse)</source>
      <translation>低内存（稀疏）</translation>
    </message>
    <message>
      <source>Use single-precision sparse operators to cut RAM (for many files / large meshes). Auto-enabled for large problems; check to force it on.</source>
      <translation>使用单精度稀疏算子以降低内存占用（适用于大量文件 / 大型网格）。大型问题会自动启用；勾选可强制启用。</translation>
    </message>
    <message>
      <source>ERT input formats</source>
      <translation>ERT 输入格式</translation>
    </message>
    <message>
      <source>Not used by this engine's time-lapse inversion: ADTLERT stops when its model step gets small, or at Max iterations.</source>
      <translation>此引擎的时移反演不使用该项：ADTLERT 在模型步长足够小或达到最大迭代次数时停止。</translation>
    </message>
    <message>
      <source>Not used: R2 and R3t decide for themselves when the inversion is done.</source>
      <translation>不使用：R2 和 R3t 自行判断反演何时完成。</translation>
    </message>
    <message>
      <source>Checking CUDA, cuDSS, NVRTC and GPU CGLS…</source>
      <translation>正在检查 CUDA、cuDSS、NVRTC 和 GPU CGLS…</translation>
    </message>
    <message>
      <source>CUDA check failed; GPU inversion is not verified. Select PyHydro CPU. {0}</source>
      <translation>CUDA 检查失败；GPU 反演未通过验证。请选择 PyHydro CPU。{0}</translation>
    </message>
    <message>
      <source>Where E4D runs. E4D is built from source (github.com/pnnl/E4D) with gfortran, PETSc and MPI, for Linux.

This computer: Linux, or macOS with a source build; e4d and mpirun are found on PATH, through PYHYDRO_E4D / PYHYDRO_MPIRUN, or from the program given below.
WSL: on Windows, E4D built inside a WSL 2 Linux distribution; the program below is then a Linux path. E4D has no Windows build of its own.
Write files only: the complete E4D run folder is written and the run stops, for a cluster or another machine: run mpirun -np N e4d in it, then read it back with inversion.e4d.read_e4d_run.</source>
      <translation>E4D 的运行位置。E4D 需从源码（github.com/pnnl/E4D）使用 gfortran、PETSc 和 MPI 在 Linux 上编译。

本机：Linux，或从源码编译的 macOS；e4d 和 mpirun 从 PATH、PYHYDRO_E4D / PYHYDRO_MPIRUN 或下方指定的程序中查找。
WSL：在 Windows 上，于 WSL 2 Linux 发行版中编译的 E4D；此时下方程序为 Linux 路径。E4D 本身没有 Windows 版本。
仅写出文件：写出完整的 E4D 运行文件夹后停止，用于集群或其他机器：在该文件夹中运行 mpirun -np N e4d，然后使用 inversion.e4d.read_e4d_run 读回结果。</translation>
    </message>
    <message>
      <source>Run E4D</source>
      <translation>运行 E4D</translation>
    </message>
    <message>
      <source>e4d on PATH</source>
      <translation>PATH 中的 e4d</translation>
    </message>
    <message>
      <source>The e4d program, when it is not on PATH: a path on this computer, or a Linux path for WSL. Leave empty to use PATH or PYHYDRO_E4D.</source>
      <translation>e4d 程序（当其不在 PATH 中时）：本机路径，或 WSL 的 Linux 路径。留空则使用 PATH 或 PYHYDRO_E4D。</translation>
    </message>
    <message>
      <source>Choose the e4d program on this computer.</source>
      <translation>选择本机上的 e4d 程序。</translation>
    </message>
    <message>
      <source>E4D program</source>
      <translation>E4D 程序</translation>
    </message>
    <message>
      <source>MPI processes for mpirun -np. E4D needs at least two - one master and one or more workers - and no more workers than electrodes.</source>
      <translation>mpirun -np 的 MPI 进程数。E4D 至少需要两个进程（一个主进程和一个或多个工作进程），且工作进程数不得多于电极数。</translation>
    </message>
    <message>
      <source>MPI processes</source>
      <translation>MPI 进程数</translation>
    </message>
    <message>
      <source>Choose the e4d program</source>
      <translation>选择 e4d 程序</translation>
    </message>
    <message>
      <source>Looking for E4D…</source>
      <translation>正在查找 E4D…</translation>
    </message>
    <message>
      <source>Whether R2/R3t is run here. They are Windows programs (R2.exe, R3t.exe) from Andrew Binley's web page or any ResIPy installation.

Auto: run natively on Windows, through Wine on Linux and macOS. The program is the one given below, else PYHYDRO_R2 / PYHYDRO_R3T, else ResIPy's copy, else the first on PATH.
Write files only: the complete run folder is written and the run stops; run R2.exe or R3t.exe in it elsewhere, then read it back with inversion.r2.read_r2_run.</source>
      <extracomment>The launcher is one choice for both programs; each has its own path.</extracomment>
      <translation>是否在本机运行 R2/R3t。它们是 Windows 程序（R2.exe、R3t.exe），可从 Andrew Binley 的网页或任意 ResIPy 安装中获取。

自动：在 Windows 上原生运行，在 Linux 和 macOS 上通过 Wine 运行。程序依次取下方指定的程序、PYHYDRO_R2 / PYHYDRO_R3T、ResIPy 自带副本、PATH 中的第一个。
仅写出文件：写出完整的运行文件夹后停止；在其他位置于该文件夹中运行 R2.exe 或 R3t.exe，然后使用 inversion.r2.read_r2_run 读回结果。</translation>
    </message>
    <message>
      <source>Run R2/R3t</source>
      <translation>运行 R2/R3t</translation>
    </message>
    <message>
      <source>ResIPy's copy, or PATH</source>
      <translation>ResIPy 自带副本或 PATH</translation>
    </message>
    <message>
      <source>The R2.exe or R3t.exe to run, when another than ResIPy's or the one on PATH. Leave empty to search for it.</source>
      <translation>要运行的 R2.exe 或 R3t.exe（当不使用 ResIPy 自带或 PATH 中的版本时）。留空则自动搜索。</translation>
    </message>
    <message>
      <source>Choose the R2 or R3t program.</source>
      <translation>选择 R2 或 R3t 程序。</translation>
    </message>
    <message>
      <source>Program</source>
      <translation>程序</translation>
    </message>
    <message>
      <source>{0}.exe from ResIPy, or PATH</source>
      <translation>来自 ResIPy 或 PATH 的 {0}.exe</translation>
    </message>
    <message>
      <source>Choose the {0} program</source>
      <translation>选择 {0} 程序</translation>
    </message>
    <message>
      <source>Looking for the program…</source>
      <translation>正在查找程序…</translation>
    </message>
    <message>
      <source>ResIPy ready</source>
      <translation>ResIPy 就绪</translation>
    </message>
    <message>
      <source>ResIPy unavailable</source>
      <translation>ResIPy 不可用</translation>
    </message>
    <message>
      <source>{0} available for loading data.</source>
      <translation>{0} 可用于载入数据。</translation>
    </message>
    <message>
      <source>ResIPy is not installed; some formats require it. See Data format.</source>
      <translation>未安装 ResIPy；部分格式需要它。请参阅“数据格式”。</translation>
    </message>
    <message>
      <source>ResIPy unavailable; some formats need it.</source>
      <translation>ResIPy 不可用；部分格式需要它。</translation>
    </message>
    <message>
      <source>Data loaded by {0}{1}.</source>
      <translation>数据由 {0}{1} 载入。</translation>
    </message>
    <message>
      <source>{0} looks like a {1} file, but is read as {2}.</source>
      <translation>{0} 看起来是 {1} 文件，但将按 {2} 读取。</translation>
    </message>
    <message>
      <source>Read as {0}</source>
      <translation>按 {0} 读取</translation>
    </message>
    <message>
      <source>All extra checks are supported by this file. A value of 0 turns each numerical check off.</source>
      <translation>该文件支持所有附加检查。数值检查设为 0 即关闭。</translation>
    </message>
    <message>
      <source>Each reading's error from a line fitted to the reciprocal pairs: log10(dR) = m·log10(R) + b, where R is a pair's mean resistance and dR the difference between its two directions, so dR = 10^b·R^m and the relative error is dR / R, never below the Minimum set below. A single inversion fits it to the survey's own pairs; a time-lapse inversion fits one line to the pairs of every survey and gives it to all of them. The Reciprocal errors tab draws the pairs and the line, and its “Fit to” chooser sets whether the line is fitted to all pairs or only to those the filter kept. The Data QC report and the settings file state the fit.</source>
      <translation>每个读数的误差由互易测量对拟合的直线确定：log10(dR) = m·log10(R) + b，其中 R 为测量对的平均电阻，dR 为正反两个方向之差，因此 dR = 10^b·R^m，相对误差为 dR / R，且不低于下方设置的最小值。单次反演用该测量自身的测量对拟合；时移反演用所有测量的测量对拟合一条直线并应用于全部测量。“互易误差”选项卡绘制测量对和直线，其“拟合对象”选项决定直线是拟合全部测量对还是仅拟合滤波保留的测量对。数据 QC 报告和设置文件会说明拟合结果。</translation>
    </message>
    <message>
      <source>Needs readings measured both ways (each reading and its reciprocal). The loaded data have none; for a survey written as two files, add both and keep “Pair reciprocal files” ticked.</source>
      <translation>需要双向测量的读数（每个读数及其互易读数）。已载入的数据中没有；若测量数据保存为两个文件，请添加这两个文件并保持勾选“配对互易文件”。</translation>
    </message>
    <message>
      <source>√(spread² + estimate²) for each reading: the scatter of its potential's samples, as a fraction of the potential, added in quadrature to the estimate below. The scatter within one reading is not its uncertainty and usually overstates it, so χ² tends to come out low; it is never the default.</source>
      <translation>每个读数取 √(spread² + estimate²)：其电位采样的离散度（以占电位的比例表示）与下方估计值按平方和合成。单个读数内部的离散度并非其不确定度，且通常偏大，因此 χ² 往往偏低；此选项从不作为默认值。</translation>
    </message>
    <message>
      <source>Needs the spread of each reading's potential samples, which the loaded data do not record (Subsurface Insights exports do).</source>
      <translation>需要每个读数电位采样的离散度，已载入的数据未记录该信息（Subsurface Insights 导出的数据包含）。</translation>
    </message>
    <message>
      <source>Load electrode file</source>
      <translation>载入电极文件</translation>
    </message>
    <message>
      <source>Import mesh…</source>
      <translation>导入网格…</translation>
    </message>
    <message>
      <source>Inverts on an externally built mesh instead of one generated from the electrode positions. PyGIMLi .bms, Gmsh .msh, VTK, .poly, or an E4D mesh (.1.node / .1.ele, with its .trn). An E4D mesh configuration (.cfg) is meshed once, on import. The region to invert must carry marker 2 or above; marker 0 and 1 are treated as background and stay fixed - for an E4D mesh, zone 1 is the background. The file is checked against the survey before the run starts.</source>
      <translation>在外部构建的网格上反演，而非由电极位置生成的网格。支持 PyGIMLi .bms、Gmsh .msh、VTK、.poly 或 E4D 网格（.1.node / .1.ele 及其 .trn）。E4D 网格配置（.cfg）在导入时剖分一次。待反演区域的标记须为 2 或以上；标记 0 和 1 视为背景并保持固定——对于 E4D 网格，分区 1 为背景。运行开始前会根据测量数据检查该文件。</translation>
    </message>
    <message>
      <source>Go back to a mesh generated from the data.</source>
      <translation>恢复为由数据生成的网格。</translation>
    </message>
    <message>
      <source>Source</source>
      <translation>来源</translation>
    </message>
    <message>
      <source>Built from the electrode positions.</source>
      <translation>由电极位置构建。</translation>
    </message>
    <message>
      <source>Build a 3D mesh…</source>
      <translation>构建三维网格…</translation>
    </message>
    <message>
      <source>Open the 3D Mesh Builder with these electrodes - a profile as a line at y = 0 - to build a 3D mesh around them with PyGIMLi, Gmsh or the E4D mesher. Its Use for ERT inversion button brings the mesh back here as the imported mesh, shown in 3D on this tab.</source>
      <translation>使用这些电极（剖面作为 y = 0 处的直线）打开三维网格构建器，以便用 PyGIMLi、Gmsh 或 E4D 网格生成器围绕电极构建三维网格。其“用于 ERT 反演”按钮会将网格作为导入网格带回此处，并在此选项卡中以三维显示。</translation>
    </message>
    <message>
      <source>How deep to invert. PyGIMLi sizes the parameter domain from the array length, which for a long line reaches well below anything the data resolve; capping it removes unknowns the inversion cannot constrain and shortens every iteration. Leave at auto unless the sensitivity plot shows the bottom of the section is empty. Auto is 0.4 times the electrode spread (PyGIMLi's paraDepth).</source>
      <translation>反演深度。PyGIMLi 根据排列长度确定参数区域，对于长测线而言远深于数据可分辨的范围；限制深度可去除反演无法约束的未知量，并缩短每次迭代的时间。除非灵敏度图显示断面底部为空，否则保持自动。自动值为电极排列长度的 0.4 倍（PyGIMLi 的 paraDepth）。</translation>
    </message>
    <message>
      <source>Depth</source>
      <translation>深度</translation>
    </message>
    <message>
      <source> spacings</source>
      <translation> 个间距</translation>
    </message>
    <message>
      <source>How far the inverted region reaches past the first and the last electrode, in electrode spacings. A wider margin lets the inversion put structure beside the line rather than forcing it under the end electrodes, at the cost of cells the data barely see. PyGIMLi's paraBoundary, 2 by default; the padding of E4D's fine zone.</source>
      <translation>反演区域超出首尾电极的范围，以电极间距为单位。边距越宽，反演越能将结构置于测线两侧，而不是强行压在端部电极下方，代价是增加数据几乎无法感知的单元。即 PyGIMLi 的 paraBoundary，默认为 2；对应 E4D 精细区的外扩。</translation>
    </message>
    <message>
      <source>Side margin</source>
      <translation>侧边距</translation>
    </message>
    <message>
      <source> between electrodes</source>
      <translation> 电极间</translation>
    </message>
    <message>
      <source>Mesh nodes placed on the surface between two neighbouring electrodes. More give smaller cells near the surface, where the data resolve the most, and more unknowns. PyGIMLi's addNodes; 1, a node halfway between electrodes, by default.</source>
      <translation>在相邻两电极之间的地表上放置的网格节点数。数量越多，近地表（数据分辨率最高处）的单元越小，未知数也越多。对应 PyGIMLi 的 addNodes；默认为 1，即在电极中点放置一个节点。</translation>
    </message>
    <message>
      <source>Surface nodes</source>
      <translation>地表节点</translation>
    </message>
    <message>
      <source>no limit</source>
      <translation>无限制</translation>
    </message>
    <message>
      <source>Upper limit on the area of an inverted cell. Without one the cells grow with depth; a limit keeps them small and even, with many more unknowns. The line under the plot gives the cell sizes of the mesh shown. PyGIMLi's paraMaxCellSize; the maximum volume of E4D's fine zone.</source>
      <translation>反演单元面积的上限。不设上限时单元随深度增大；设上限可使单元小而均匀，但未知数会大大增加。图下方一行给出所示网格的单元尺寸。对应 PyGIMLi 的 paraMaxCellSize，以及 E4D 精细区的最大体积。</translation>
    </message>
    <message>
      <source>Largest cell</source>
      <translation>最大单元</translation>
    </message>
    <message>
      <source>The smallest angle a triangle may have. Higher gives better-shaped triangles and more of them; Triangle cannot finish much above 34°, so that is the limit. PyGIMLi's quality; E4D sets the same for TetGen.</source>
      <translation>三角形允许的最小角。值越大，三角形形状越好、数量越多；Triangle 在明显高于 34° 时无法完成，因此以此为上限。对应 PyGIMLi 的 quality；E4D 为 TetGen 设置相同参数。</translation>
    </message>
    <message>
      <source>Quality</source>
      <translation>质量</translation>
    </message>
    <message>
      <source> × spread</source>
      <translation> × 排列长度</translation>
    </message>
    <message>
      <source>auto (4 × spread)</source>
      <translation>自动（4 × 排列长度）</translation>
    </message>
    <message>
      <source>How far the outer region reaches beyond the inverted region, sideways and down, in lengths of the electrode spread. Too narrow and the boundary distorts the forward response; wider costs little, because its cells are large. PyGIMLi's boundary, 4 by default; E4D's outer boundary distance.</source>
      <translation>外部区域在侧向和向下超出反演区域的范围，以电极排列长度为单位。过窄会使边界扭曲正演响应；加宽代价很小，因为其单元较大。即 PyGIMLi 的 boundary，默认为 4；对应 E4D 的外边界距离。</translation>
    </message>
    <message>
      <source>Width</source>
      <translation>宽度</translation>
    </message>
    <message>
      <source>Upper limit on the cell area in the outer region. Leave it unlimited unless the forward solution needs a finer outer mesh: these cells are never inverted. PyGIMLi's boundaryMaxCellSize; the maximum volume of E4D's outer zone.</source>
      <translation>外部区域单元面积的上限。除非正演求解需要更细的外部网格，否则保持不限：这些单元从不参与反演。对应 PyGIMLi 的 boundaryMaxCellSize，以及 E4D 外部区的最大体积。</translation>
    </message>
    <message>
      <source>Restore defaults</source>
      <translation>恢复默认</translation>
    </message>
    <message>
      <source>Put every setting above back to PyGIMLi's default mesh. The imported mesh and the zones are left alone.</source>
      <translation>将以上所有设置恢复为 PyGIMLi 的默认网格设置。导入的网格和分区保持不变。</translation>
    </message>
    <message>
      <source>Import inversion mesh</source>
      <translation>导入反演网格</translation>
    </message>
    <message>
      <source>&lt;span style='color:{0}'&gt;{1}: {2}&lt;/span&gt;</source>
      <translation>&lt;span style='color:{0}'&gt;{1}：{2}&lt;/span&gt;</translation>
    </message>
    <message>
      <source>Building the mesh {0} describes, as E4D would…</source>
      <translation>正在按 E4D 的方式构建 {0} 所描述的网格…</translation>
    </message>
    <message>
      <source>Add ERT data file(s)</source>
      <translation>添加 ERT 数据文件</translation>
    </message>
    <message>
      <source>{0} surveys selected — Remove / Move ↑ ↓, or click one to preview.</source>
      <translation>已选择 {0} 期测量——可移除 / 上移 ↑ 下移 ↓，或单击某项预览。</translation>
    </message>
    <message>
      <source>Export time-lapse results to folder</source>
      <translation>导出时移结果到文件夹</translation>
    </message>
    <message>
      <source>{0}. Add data files to see the pseudosection.</source>
      <translation>{0}。添加数据文件以查看拟断面。</translation>
    </message>
    <message>
      <source>{0:,} readings, {1:.3g}–{2:.3g} Ω·m   ▼ electrodes</source>
      <translation>{0:,} 个读数，{1:.3g}–{2:.3g} Ω·m   ▼ 电极</translation>
    </message>
    <message>
      <source>{0}&lt;br&gt;Measurements: {1:,}&lt;br&gt;Data: {2}{3}{4}{5}{6}</source>
      <translation>{0}&lt;br&gt;测量数：{1:,}&lt;br&gt;数据：{2}{3}{4}{5}{6}</translation>
    </message>
    <message>
      <source>Export electrodes</source>
      <translation>导出电极</translation>
    </message>
    <message>
      <source>Export geometry</source>
      <translation>导出几何</translation>
    </message>
    <message>
      <source>Export resistivity model to folder</source>
      <translation>导出电阻率模型到文件夹</translation>
    </message>
    <message>
      <source>Layers the rock physics is set for</source>
      <extracomment>The steps the assistant names. Each opens the view and the panel the step is done in (see _go_to); the page itself does not page through them. The "Use example" model bundle, under the source repository's examples/: the Treeline time-lapse ERT model of Ex_MC_Hydro, whose two layers the default rock physics (ERT_to_WC.DEFAULT_LAYER_DISTRIBUTIONS) was set for. The coverage (log10) under which cells are blanked, on the view and in the maps. Fill of the layers on the Layers view, in marker order; a layer that is not estimated is drawn in the last, neutral one.</extracomment>
      <translation>已设置岩石物理参数的层</translation>
    </message>
    <message>
      <source>Results</source>
      <translation>结果</translation>
    </message>
    <message>
      <source>Time series</source>
      <translation>时间序列</translation>
    </message>
    <message>
      <source>Use project data</source>
      <translation>使用工程数据</translation>
    </message>
    <message>
      <source>Use example</source>
      <translation>使用示例</translation>
    </message>
    <message>
      <source>Load this project's inverted ERT model.</source>
      <translation>载入本工程已反演的 ERT 模型。</translation>
    </message>
    <message>
      <source>Load the Treeline time-lapse ERT model of the Ex_MC_Hydro example: 12 surveys over regolith and bedrock.</source>
      <translation>载入 Ex_MC_Hydro 示例中的 Treeline 时移 ERT 模型：覆盖风化层和基岩的 12 次测量。</translation>
    </message>
    <message>
      <source>Open folder…</source>
      <translation>打开文件夹…</translation>
    </message>
    <message>
      <source>Estimate water content from an ERT model</source>
      <translation>由 ERT 模型估算含水量</translation>
    </message>
    <message>
      <source>Turn an inverted, time-lapse ERT resistivity model into water content, with its uncertainty, through rock physics sampled many times over.</source>
      <translation>通过多次采样的岩石物理关系，将反演得到的时移 ERT 电阻率模型转换为含水量及其不确定度。</translation>
    </message>
    <message>
      <source>Load an inverted ERT model: its mesh, resistivity and layers.</source>
      <translation>载入已反演的 ERT 模型：包括网格、电阻率和层。</translation>
    </message>
    <message>
      <source>Tick the layers to estimate in, and check each one's rock physics.</source>
      <translation>勾选要进行估算的层，并检查每层的岩石物理参数。</translation>
    </message>
    <message>
      <source>Press Estimate water content.</source>
      <translation>请点击“估算含水量”。</translation>
    </message>
    <message>
      <source>The survey of the time-lapse series shown here and in the result maps. Every survey is estimated.</source>
      <translation>此处及结果地图中显示的时移序列测量。每次测量都会进行估算。</translation>
    </message>
    <message>
      <source>Survey</source>
      <translation>测量</translation>
    </message>
    <message>
      <source>Water content through the surveys at two points, with the ±1σ band the rock-physics uncertainty gives it.</source>
      <translation>两个点处各期测量的含水量，以及由岩石物理不确定度给出的 ±1σ 区间。</translation>
    </message>
    <message>
      <source>Plot</source>
      <translation>绘图</translation>
    </message>
    <message>
      <source>Estimate water content</source>
      <extracomment>Each numbered step's title; a finished step gets a tick after it.</extracomment>
      <translation>估算含水量</translation>
    </message>
    <message>
      <source>Sample each layer's rock physics many times, turn every survey's resistivity into water content with each sample, and map the mean and the spread.</source>
      <translation>对每层的岩石物理参数进行多次抽样，用每个样本将每次测量的电阻率转换为含水量，并绘制均值和离散度。</translation>
    </message>
    <message>
      <source>1  Inverted ERT model</source>
      <translation>1  ERT 反演模型</translation>
    </message>
    <message>
      <source>Open an ERT inversion's output folder, or a folder with mesh_res.bms, resmodel.npy and index_marker.npy (all_coverage.npy is optional).</source>
      <translation>打开 ERT 反演的输出文件夹，或包含 mesh_res.bms、resmodel.npy 和 index_marker.npy 的文件夹（all_coverage.npy 为可选）。</translation>
    </message>
    <message>
      <source>Read the folder again, after its files changed.</source>
      <translation>在文件夹中的文件变更后重新读取该文件夹。</translation>
    </message>
    <message>
      <source>What the folder must contain.</source>
      <translation>文件夹必须包含的内容。</translation>
    </message>
    <message>
      <source>2  Layers</source>
      <translation>2  分层</translation>
    </message>
    <message>
      <source>Tick the layers to estimate water content in, and name them as you like. The Layers tab shows where they are.</source>
      <translation>勾选要估算含水量的层，并可自由命名。“分层”标签页显示其位置。</translation>
    </message>
    <message>
      <source>Layers from a seismic bedrock interface…</source>
      <translation>由地震基岩界面生成层…</translation>
    </message>
    <message>
      <source>Split the model into regolith (above) and bedrock (below) along a bedrock interface: the one sent from Seismic → Structure, or one read from a file.</source>
      <translation>沿基岩界面将模型划分为风化层（上）和基岩（下）：界面可来自 地震 → 构造，或从文件读取。</translation>
    </message>
    <message>
      <source>Back to the layers in the file</source>
      <translation>恢复为文件中的分层</translation>
    </message>
    <message>
      <source>Use the model's own index_marker.npy again, with its layers ticked and named as they start.</source>
      <translation>重新使用模型自带的 index_marker.npy，各层按初始状态勾选和命名。</translation>
    </message>
    <message>
      <source>3  Rock physics</source>
      <translation>3  岩石物理</translation>
    </message>
    <message>
      <source>How resistivity becomes water content in each ticked layer. Each value is a mean ± spread, sampled many times so the result carries its uncertainty. Unfold a layer to change them.</source>
      <translation>各勾选层中电阻率转换为含水量的方式。每个值为均值 ± 离散度，经多次抽样，使结果包含其不确定性。展开某层可修改这些值。</translation>
    </message>
    <message>
      <source>4  Estimate</source>
      <translation>4  估算</translation>
    </message>
    <message>
      <source>Porosity instead of water content, for ground of known saturation (1 = saturated).</source>
      <translation>以孔隙度代替含水量，适用于饱和度已知的地层（1 = 饱和）。</translation>
    </message>
    <message>
      <source>Assumed saturation</source>
      <translation>假定饱和度</translation>
    </message>
    <message>
      <source>Samples</source>
      <translation>样本数</translation>
    </message>
    <message>
      <source>Random seed</source>
      <translation>随机种子</translation>
    </message>
    <message>
      <source>Tortuosity a</source>
      <translation>迂曲度 a</translation>
    </message>
    <message>
      <source>Map colours</source>
      <translation>地图颜色</translation>
    </message>
    <message>
      <source>Save rock-physics settings</source>
      <translation>保存岩石物理设置</translation>
    </message>
    <message>
      <source>Write the layers and their rock physics to petro_config.json, without estimating anything.</source>
      <translation>将各层及其岩石物理参数写入 petro_config.json，不进行任何估算。</translation>
    </message>
    <message>
      <source>ERT → Water Content input format</source>
      <translation>ERT → 含水量输入格式</translation>
    </message>
    <message>
      <source>Select inverted-model folder</source>
      <translation>选择反演模型文件夹</translation>
    </message>
    <message>
      <source>No model loaded. Open an ERT inversion's output folder, or a folder with mesh_res.bms, resmodel.npy and index_marker.npy, or use the example.</source>
      <translation>未载入模型。请打开 ERT 反演的输出文件夹，或包含 mesh_res.bms、resmodel.npy 和 index_marker.npy 的文件夹，或使用示例。</translation>
    </message>
    <message>
      <source>Could not read the model: {0}</source>
      <translation>无法读取模型：{0}</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0}&lt;/b&gt;&lt;br&gt;{1} survey{2} · {3:,} cells · {4} layer{5}</source>
      <translation>&lt;b&gt;{0}&lt;/b&gt;&lt;br&gt;{1} 次测量 · {3:,} 个单元 · {4} 层</translation>
    </message>
    <message>
      <source>of 0–{0}</source>
      <translation>（共 0–{0}）</translation>
    </message>
    <message>
      <source>(one survey)</source>
      <translation>（单次测量）</translation>
    </message>
    <message>
      <source>The model could not be drawn: {0}</source>
      <translation>无法绘制模型：{0}</translation>
    </message>
    <message>
      <source>marker {0} · {1:,} cells</source>
      <translation>标记 {0} · {1:,} 个单元</translation>
    </message>
    <message>
      <source>Load bedrock interface (x, z)</source>
      <translation>载入基岩界面 (x, z)</translation>
    </message>
    <message>
      <source>Tick a layer in 2 to set its rock physics.</source>
      <translation>在第 2 步中勾选一层以设置其岩石物理参数。</translation>
    </message>
    <message>
      <source>Change</source>
      <translation>更改</translation>
    </message>
    <message>
      <source>&lt;b&gt;Mean&lt;/b&gt;</source>
      <translation>&lt;b&gt;均值&lt;/b&gt;</translation>
    </message>
    <message>
      <source>&lt;b&gt;± spread&lt;/b&gt;</source>
      <translation>&lt;b&gt;± 离散度&lt;/b&gt;</translation>
    </message>
    <message>
      <source>porosity {0}, m {1}, n {2}, pore water {3} Ω·m</source>
      <translation>孔隙度 {0}，m {1}，n {2}，孔隙水 {3} Ω·m</translation>
    </message>
    <message>
      <source>Nothing was estimated; the rock-physics settings were saved instead.</source>
      <translation>未进行估算；已改为保存岩石物理设置。</translation>
    </message>
    <message>
      <source>Estimated {0} from {1} samples of the rock physics, for {2} surveys. The maps show survey {3}.</source>
      <translation>基于 {1} 个岩石物理样本，估算了 {2} 次测量的{0}。图中显示测量 {3}。</translation>
    </message>
    <message>
      <source>Water content (-)</source>
      <translation>含水量 (-)</translation>
    </message>
    <message>
      <source>Point {0} (cell {1})</source>
      <translation>点 {0}（单元 {1}）</translation>
    </message>
    <message>
      <source>Estimating…</source>
      <translation>正在估算…</translation>
    </message>
    <message>
      <source>Starting the estimate…</source>
      <translation>正在开始估计…</translation>
    </message>
    <message>
      <source>Finished. The maps are on the Results tab.</source>
      <translation>已完成。图件位于“结果”选项卡。</translation>
    </message>
    <message>
      <source>The estimate failed: {0}</source>
      <translation>估算失败：{0}</translation>
    </message>
    <message>
      <source>Stopped before it finished. Press Estimate water content to start again.</source>
      <translation>未完成即已停止。按“估算含水量”重新开始。</translation>
    </message>
    <message>
      <source>Depth and elevation use the velocity on the right; elevation also needs the ground elevations.</source>
      <extracomment>Where the "Use example" model lives under the source repository's examples/.</extracomment>
      <translation>深度和高程使用右侧的速度；高程还需要地面高程。</translation>
    </message>
    <message>
      <source>Vertical</source>
      <translation>垂直</translation>
    </message>
    <message>
      <source>The trace shown; clicking the radargram picks one too.</source>
      <translation>显示的道；点击雷达剖面也可选择道。</translation>
    </message>
    <message>
      <source>Trace</source>
      <translation>道</translation>
    </message>
    <message>
      <source>Load GPR data</source>
      <translation>载入 GPR 数据</translation>
    </message>
    <message>
      <source>No GPR line loaded</source>
      <translation>未载入 GPR 测线</translation>
    </message>
    <message>
      <source>Open file…</source>
      <translation>打开文件…</translation>
    </message>
    <message>
      <source>Simulate a 100 MHz GPR line over the MODFLOW catchment model.</source>
      <translation>在 MODFLOW 流域模型上模拟一条 100 MHz GPR 测线。</translation>
    </message>
    <message>
      <source>No line loaded.</source>
      <translation>未载入测线。</translation>
    </message>
    <message>
      <source>Line geometry</source>
      <translation>测线几何</translation>
    </message>
    <message>
      <source>Trace spacing</source>
      <translation>道间距</translation>
    </message>
    <message>
      <source>Antenna frequency</source>
      <translation>天线频率</translation>
    </message>
    <message>
      <source>Dewow (remove slow drift)</source>
      <translation>Dewow（去除低频漂移）</translation>
    </message>
    <message>
      <source>Subtracts each trace's running mean: the low-frequency swing a receiver adds under the first arrivals.</source>
      <translation>减去每道的滑动平均值，即接收器在初至下方叠加的低频漂移。</translation>
    </message>
    <message>
      <source>    Window</source>
      <translation>    窗口</translation>
    </message>
    <message>
      <source>Time-zero correction</source>
      <translation>零时校正</translation>
    </message>
    <message>
      <source>Moves time zero onto the direct wave, so times and depths count from the ground surface. The samples before it are dropped.</source>
      <translation>将零时刻移到直达波处，使时间和深度从地表起算。其之前的采样点将被舍弃。</translation>
    </message>
    <message>
      <source>Pick automatically</source>
      <translation>自动拾取</translation>
    </message>
    <message>
      <source>Type it in</source>
      <translation>手动输入</translation>
    </message>
    <message>
      <source>    Time zero</source>
      <translation>    零时刻</translation>
    </message>
    <message>
      <source>    At</source>
      <translation>    位置</translation>
    </message>
    <message>
      <source>Band-pass filter</source>
      <translation>带通滤波</translation>
    </message>
    <message>
      <source>Keeps the frequencies the antenna sends and removes the rest. Check the band on the Spectrum view.</source>
      <translation>保留天线发射的频率并去除其余频率。请在频谱视图中检查频带。</translation>
    </message>
    <message>
      <source>    Low</source>
      <translation>    低</translation>
    </message>
    <message>
      <source>    High</source>
      <translation>    高</translation>
    </message>
    <message>
      <source>Background removal</source>
      <translation>背景去除</translation>
    </message>
    <message>
      <source>Subtracts the average trace: removes the antenna's ringing and the direct wave, which repeat on every trace. It also removes flat reflectors as long as the line.</source>
      <translation>减去平均道：去除每道都重复出现的天线振铃和直达波。与测线等长的水平反射层也会被一并去除。</translation>
    </message>
    <message>
      <source>whole line</source>
      <translation>整条测线</translation>
    </message>
    <message>
      <source>How many neighbouring traces are averaged. The whole line is usual; a few hundred traces keep long dipping layers.</source>
      <translation>参与平均的相邻道数。通常取整条测线；取几百道可保留延伸较长的倾斜层。</translation>
    </message>
    <message>
      <source>    Average over</source>
      <translation>    平均范围</translation>
    </message>
    <message>
      <source>Velocity / depth</source>
      <translation>速度 / 深度</translation>
    </message>
    <message>
      <source>Velocity</source>
      <translation>速度</translation>
    </message>
    <message>
      <source>Relative permittivity</source>
      <translation>相对介电常数</translation>
    </message>
    <message>
      <source>Fit a hyperbola</source>
      <translation>拟合双曲线</translation>
    </message>
    <message>
      <source>Then click the top of a hyperbola on the radargram.</source>
      <translation>然后点击雷达剖面上双曲线的顶点。</translation>
    </message>
    <message>
      <source>Ground elevations…</source>
      <translation>地面高程…</translation>
    </message>
    <message>
      <source>A CSV of distance and elevation (m) along the line, for the Elevation view.</source>
      <translation>沿测线的距离与高程（m）CSV 文件，用于高程视图。</translation>
    </message>
    <message>
      <source>Migration</source>
      <translation>偏移</translation>
    </message>
    <message>
      <source>F-K migration</source>
      <translation>F-K 偏移</translation>
    </message>
    <message>
      <source>Moves each diffraction back to the point that made it, with the velocity above. Fit the velocity first: a wrong one leaves smiles or frowns.</source>
      <translation>使用上方的速度将每个绕射归位到其产生点。请先拟合速度：速度错误会残留上凹或下凹弧形。</translation>
    </message>
    <message>
      <source>Gain</source>
      <translation>增益</translation>
    </message>
    <message>
      <source>None</source>
      <translation>无</translation>
    </message>
    <message>
      <source>none</source>
      <translation>无</translation>
    </message>
    <message>
      <source>Power of time</source>
      <translation>时间幂次</translation>
    </message>
    <message>
      <source>Automatic gain control</source>
      <translation>自动增益控制</translation>
    </message>
    <message>
      <source>Brings up the late, weak reflections so they can be seen. Automatic gain makes everything about as strong, so amplitudes are no longer comparable.</source>
      <translation>增强晚期弱反射使其可见。自动增益会使各处强度大致相当，因此振幅不再具有可比性。</translation>
    </message>
    <message>
      <source>    Power</source>
      <translation>    幂次</translation>
    </message>
    <message>
      <source>View processed radargram</source>
      <translation>查看处理后的雷达剖面</translation>
    </message>
    <message>
      <source>Save results…</source>
      <translation>保存结果…</translation>
    </message>
    <message>
      <source>Writes the processed line (.npz), the radargram as shown (.png) and the processing recipe (.json) to a folder.</source>
      <translation>将处理后的测线 (.npz)、当前显示的雷达剖面 (.png) 和处理配方 (.json) 写入文件夹。</translation>
    </message>
    <message>
      <source>Processing…</source>
      <translation>正在处理…</translation>
    </message>
    <message>
      <source>Open a GPR line</source>
      <translation>打开 GPR 测线</translation>
    </message>
    <message>
      <source>Could not read {0}: {1}</source>
      <translation>无法读取 {0}：{1}</translation>
    </message>
    <message>
      <source>Ground elevations along the line</source>
      <translation>沿测线的地面高程</translation>
    </message>
    <message>
      <source>Ground elevations from {0}.</source>
      <translation>地面高程来自 {0}。</translation>
    </message>
    <message>
      <source>No ground elevations: the Elevation view is off.</source>
      <translation>无地面高程：高程视图已关闭。</translation>
    </message>
    <message>
      <source>{0} step{1} applied in {2:.2f} s.</source>
      <translation>已应用 {0} 个步骤，用时 {2:.2f} s。</translation>
    </message>
    <message>
      <source>Processing stopped: {0}</source>
      <translation>处理已停止：{0}</translation>
    </message>
    <message>
      <source>Two-way time (ns)</source>
      <translation>双程时间 (ns)</translation>
    </message>
    <message>
      <source>Trace {0} at {1:.2f} {2} - as recorded</source>
      <translation>第 {0} 道，位于 {1:.2f} {2}（原始记录）</translation>
    </message>
    <message>
      <source>Processed</source>
      <translation>已处理</translation>
    </message>
    <message>
      <source>Amplitude</source>
      <translation>振幅</translation>
    </message>
    <message>
      <source>Frequency (MHz)</source>
      <translation>频率 (MHz)</translation>
    </message>
    <message>
      <source>Amplitude (dB, each curve's peak at 0)</source>
      <translation>振幅（dB，各曲线峰值归为 0）</translation>
    </message>
    <message>
      <source>Click the top of a hyperbola on the processed radargram.</source>
      <translation>在处理后的雷达剖面上点击双曲线顶点。</translation>
    </message>
    <message>
      <source>Adjust velocity until the dashed curve follows the hyperbola, then choose Depth below the plot.</source>
      <translation>调整速度直至虚线与双曲线吻合，然后在图下方选择“深度”。</translation>
    </message>
    <message>
      <source>Fit a hyperbola, then choose Depth below the plot. A curve that is too narrow needs a higher velocity.</source>
      <translation>先拟合双曲线，然后在图下方选择“深度”。曲线过窄时需提高速度。</translation>
    </message>
    <message>
      <source>Save the GPR results to folder</source>
      <translation>将 GPR 结果保存到文件夹</translation>
    </message>
    <message>
      <source>GPR data format</source>
      <translation>GPR 数据格式</translation>
    </message>
    <message>
      <source>Station map</source>
      <translation>测点地图</translation>
    </message>
    <message>
      <source>Data QC</source>
      <translation>数据质量控制 (QC)</translation>
    </message>
    <message>
      <source>Inversion model</source>
      <translation>反演模型</translation>
    </message>
    <message>
      <source>Load station data</source>
      <translation>载入测点数据</translation>
    </message>
    <message>
      <source>Load stations…</source>
      <translation>载入测点…</translation>
    </message>
    <message>
      <source>Field type</source>
      <translation>场类型</translation>
    </message>
    <message>
      <source>Upload x, y, value and optionally z_m (positive-up station elevation). Gravity is mGal; magnetics is nT. Use Data QC before inversion.</source>
      <translation>上传 x、y、value，以及可选的 z_m（测点高程，向上为正）。重力单位为 mGal，磁法单位为 nT。反演前请使用“数据质量控制”。</translation>
    </message>
    <message>
      <source>Ambient field (magnetics)</source>
      <translation>背景场（磁法）</translation>
    </message>
    <message>
      <source>Strength (nT)</source>
      <translation>强度 (nT)</translation>
    </message>
    <message>
      <source>Inclination (°)</source>
      <translation>倾角 (°)</translation>
    </message>
    <message>
      <source>Declination (°)</source>
      <translation>磁偏角 (°)</translation>
    </message>
    <message>
      <source>3D inversion</source>
      <translation>3D 反演</translation>
    </message>
    <message>
      <source>Inverts the uploaded field for a subsurface model: gravity → density contrast (g/cc), magnetics → susceptibility (SI). Slice the result at different depths and positions in the Inversion model tab.</source>
      <translation>将上传的场数据反演为地下模型：重力 → 密度差（g/cc），磁法 → 磁化率（SI）。可在“反演模型”选项卡中按不同深度和位置对结果切片。</translation>
    </message>
    <message>
      <source>Gravity and magnetic sensitivities do not depend on the model, so the objective is quadratic and one linear solve is the exact minimizer for a given β. That is the Linear solver: no Gauss-Newton loop, no line search, and a β sweep costs one solve per trial. SimPEG directives runs the iterative inverse problem with β cooling, kept as a cross-check and for properly bound-constrained work.</source>
      <translation>重力和磁法的灵敏度与模型无关，因此目标函数为二次型，对于给定的 β，一次线性求解即可得到精确最小值。这就是线性求解器：无需 Gauss-Newton 循环和线搜索，β 扫描每次试算只需一次求解。SimPEG directives 以 β 冷却方式运行迭代反演，保留用于交叉验证以及严格的边界约束反演。</translation>
    </message>
    <message>
      <source>Remove a polynomial regional trend before inverting (0 = none, 1 = linear, 2 = quadratic). Inversion works on the residual anomaly.</source>
      <translation>反演前去除多项式区域趋势（0 = 不去除，1 = 线性，2 = 二次）。反演基于剩余异常进行。</translation>
    </message>
    <message>
      <source>Gauss-Newton iterations. Used by the SimPEG solver only; the linear solver reaches the minimum in a single step.</source>
      <translation>Gauss-Newton 迭代次数。仅用于 SimPEG 求解器；线性求解器一步即可达到最小值。</translation>
    </message>
    <message>
      <source>Depth weighting exponent applied to the model term as sqrt(diag(JᵀWᵀWJ)) raised to this power. Without it the recovered body plasters against the top of the mesh, because shallow cells buy misfit reduction most cheaply. 0 turns the weighting off.</source>
      <translation>应用于模型项的深度加权指数，权重为 sqrt(diag(JᵀWᵀWJ)) 的该次幂。若不加权，反演得到的异常体会贴附在网格顶部，因为浅部单元降低拟合差的代价最小。设为 0 则关闭加权。</translation>
    </message>
    <message>
      <source>Used only when the loaded table has no fourth z_m column.</source>
      <translation>仅在载入的表格没有第四列 z_m 时使用。</translation>
    </message>
    <message>
      <source>How many stations the inversion uses. "all" uses every station with a value. A number thins a larger survey to an evenly spread subset, for a quicker test run; the Run group says how many it leaves out.</source>
      <translation>反演使用的测点数量。"all" 使用所有有值的测点。数值会将较大的测量抽稀为均匀分布的子集，用于快速试运行；“运行”组会显示排除了多少个。</translation>
    </message>
    <message>
      <source>Using global station elevation.</source>
      <translation>使用全局测点高程。</translation>
    </message>
    <message>
      <source>Detrend degree</source>
      <translation>去趋势阶数</translation>
    </message>
    <message>
      <source>Station elevation (m)</source>
      <translation>测点高程 (m)</translation>
    </message>
    <message>
      <source>Elevation source</source>
      <translation>高程来源</translation>
    </message>
    <message>
      <source>Mesh cells</source>
      <translation>网格单元</translation>
    </message>
    <message>
      <source>Depth weighting</source>
      <translation>深度加权</translation>
    </message>
    <message>
      <source>Assumed relative data error, applied to each station's own value.</source>
      <translation>假定的相对数据误差，应用于每个测点自身的数值。</translation>
    </message>
    <message>
      <source>Absolute error added to every station. It sets the error bar where the anomaly is near zero, which is where a flat percentage is meaningless.</source>
      <translation>加到每个测点上的绝对误差。它决定异常接近零处的误差棒，而在这些位置固定百分比误差没有意义。</translation>
    </message>
    <message>
      <source>Max stations</source>
      <translation>最大测点数</translation>
    </message>
    <message>
      <source>Auto-β: re-solve to reach target χ²</source>
      <translation>自动 β：重新求解以达到目标 χ²</translation>
    </message>
    <message>
      <source>β is not λ: it carries the data units and the mesh scale, so a sensible value cannot be guessed and is estimated from the problem instead. The search brackets and bisects it. Each trial is one linear solve, which is why this is affordable here in a way it is not for a nonlinear method.</source>
      <translation>β 不同于 λ：它包含数据单位和网格尺度，因此无法凭经验猜出合理值，而是根据问题本身估算。搜索过程先确定区间再二分。每次试算只需一次线性求解，因此在此处计算代价可以接受，而对非线性方法则不然。</translation>
    </message>
    <message>
      <source>χ² = 1 means the model explains the field to within the assumed error.</source>
      <translation>χ² = 1 表示模型在假定误差范围内解释了场数据。</translation>
    </message>
    <message>
      <source>Upper bound on the extra solves the β search may run, on top of the one at the estimated starting β.</source>
      <translation>β 搜索可额外运行的求解次数上限（不含以估算的初始 β 进行的求解）。</translation>
    </message>
    <message>
      <source>Max β trials</source>
      <translation>最大 β 试算次数</translation>
    </message>
    <message>
      <source>Run 3D inversion</source>
      <translation>运行三维反演</translation>
    </message>
    <message>
      <source>Export model…</source>
      <translation>导出模型…</translation>
    </message>
    <message>
      <source>Save the recovered 3D model as CSV (one row per voxel, with its centre and extent) plus the raw .npz, to a folder you choose.</source>
      <translation>将恢复的三维模型保存为 CSV（每个体素一行，含中心和范围）以及原始 .npz，存放到所选文件夹。</translation>
    </message>
    <message>
      <source>Export 3D model to folder</source>
      <translation>导出三维模型到文件夹</translation>
    </message>
    <message>
      <source>Colour scale ({0})</source>
      <translation>色阶 ({0})</translation>
    </message>
    <message>
      <source>Colour scale (mGal)</source>
      <translation>色阶 (mGal)</translation>
    </message>
    <message>
      <source>Map field:</source>
      <translation>地图字段：</translation>
    </message>
    <message>
      <source>Pick profile endpoints</source>
      <translation>拾取剖面端点</translation>
    </message>
    <message>
      <source>Click two points on the map to extract a profile.</source>
      <translation>在地图上点击两点以提取剖面。</translation>
    </message>
    <message>
      <source>Reset profile</source>
      <translation>重置剖面</translation>
    </message>
    <message>
      <source>Load station data to calculate QC maps.</source>
      <translation>载入测点数据以计算质量控制 (QC) 图。</translation>
    </message>
    <message>
      <source>Anomaly</source>
      <translation>异常</translation>
    </message>
    <message>
      <source>QC unavailable: {0}</source>
      <translation>QC 不可用：{0}</translation>
    </message>
    <message>
      <source>{0} anomaly ({1})</source>
      <translation>{0}异常（{1}）</translation>
    </message>
    <message>
      <source>Anomaly ({0})</source>
      <translation>异常（{0}）</translation>
    </message>
    <message>
      <source>Degree-{0} detrend · {1}: min {2:.4g}, max {3:.4g}, mean {4:.4g}, std {5:.4g} {6}.</source>
      <translation>{0} 阶去趋势 · {1}：最小值 {2:.4g}，最大值 {3:.4g}，均值 {4:.4g}，标准差 {5:.4g} {6}。</translation>
    </message>
    <message>
      <source>Ready: SimPEG potential-field backend available.</source>
      <translation>就绪：SimPEG 位场后端可用。</translation>
    </message>
    <message>
      <source>Unavailable: install the geophysics extra (SimPEG + pymatsolver). {0}</source>
      <translation>不可用：请安装 geophysics 扩展依赖（SimPEG + pymatsolver）。{0}</translation>
    </message>
    <message>
      <source>Load station file</source>
      <translation>载入测点文件</translation>
    </message>
    <message>
      <source>Using {0}.</source>
      <translation>使用 {0}。</translation>
    </message>
    <message>
      <source>{0}&lt;br&gt;{1} stations · {2}</source>
      <translation>{0}&lt;br&gt;{1} 个测点 · {2}</translation>
    </message>
    <message>
      <source>Gravity / Magnetics input format</source>
      <translation>重力 / 磁法输入格式</translation>
    </message>
    <message>
      <source>Map</source>
      <extracomment>What the map can show, and the colour-bar label of each. What the section can show. The steps the assistant names. Each opens the view and the panel the step is done in (see _go_to); the page itself does not page through them. The ERT arrays offered: what the menu says, and the pyGIMLi scheme it makes. The three zones the rock physics is set for, from the surface down (core.hydro_profile.zone_boundaries splits the model into them). Neutral plot ink: plot canvases stay light in both appearances. The "Use example" hydrology grids, under the source repository's examples/: the MODFLOW catchment model of Ex_ERT_workflow, whose arrays sit at the top of examples/data. The section Ex_ERT_workflow takes through that catchment, as [col, row], and the water-content snapshot it uses; the example opens on both. Map cells outside the model domain, hidden on the Ground surface and Porosity maps. Files of the four the loaded folder lacks. Why the last run did not finish - its error, or that it was stopped - for the assistant, whose status would otherwise still show the result before it; "" while a run is under way or succeeded. The first end of a new line is on the map and the second is awaited. A run (or a saved configuration) has filled the Results tab.
----------
Per (mesh, velocity) path pair: the mesh, its velocity and cell outlines. Why the last run did not finish - its error, or that it was stopped - for the assistant, whose status would otherwise still show the result before it; "" while a run is under way or succeeded.</extracomment>
      <translation>地图</translation>
    </message>
    <message>
      <source>Section</source>
      <translation>断面</translation>
    </message>
    <message>
      <source>Simulate surveys on a hydrologic model</source>
      <translation>在水文模型上模拟测量</translation>
    </message>
    <message>
      <source>See what ERT, seismic, EM and gravity surveys would measure over the water in a MODFLOW or ParFlow model.</source>
      <translation>查看 ERT、地震、EM 和重力测量在 MODFLOW 或 ParFlow 模型中的水体上会测得什么。</translation>
    </message>
    <message>
      <source>Load a hydrologic model: its water content, porosity and layer surfaces.</source>
      <translation>载入水文模型：包括含水量、孔隙度和层面。</translation>
    </message>
    <message>
      <source>Draw a survey line on the model's map.</source>
      <translation>在模型地图上绘制测线。</translation>
    </message>
    <message>
      <source>Tick the surveys to simulate, and press Simulate surveys.</source>
      <translation>勾选要模拟的测量，然后按“模拟测量”。</translation>
    </message>
    <message>
      <source>The model layer the map shows, counted from the top (0).</source>
      <translation>地图显示的模型层，自顶部起算 (0)。</translation>
    </message>
    <message>
      <source>No results yet. Load a model, draw a line, choose the methods and press Simulate surveys.</source>
      <translation>尚无结果。请载入模型、绘制测线、选择方法，然后点击“模拟勘探”。</translation>
    </message>
    <message>
      <source>Simulate surveys</source>
      <extracomment>Each numbered step's title; a finished step gets a tick after it.</extracomment>
      <translation>模拟测量</translation>
    </message>
    <message>
      <source>Turn the model under the line into resistivity, velocity, conductivity and density, and simulate each ticked survey on it.</source>
      <translation>将测线下方的模型转换为电阻率、速度、电导率和密度，并在其上模拟每项勾选的测量。</translation>
    </message>
    <message>
      <source>Load the hydrologic model of this project.</source>
      <translation>载入本工程的水文模型。</translation>
    </message>
    <message>
      <source>Load the MODFLOW catchment model of the Ex_ERT_workflow example, on its time step and survey line.</source>
      <translation>载入 Ex_ERT_workflow 示例中的 MODFLOW 流域模型，使用其时间步和测线。</translation>
    </message>
    <message>
      <source>1  Hydrologic model</source>
      <translation>1  水文模型</translation>
    </message>
    <message>
      <source>Open a folder with Watercontent.npy, Porosity.npy, top.npy and bot.npy.</source>
      <translation>打开包含 Watercontent.npy、Porosity.npy、top.npy 和 bot.npy 的文件夹。</translation>
    </message>
    <message>
      <source>The saved time of the model the surveys are simulated on.</source>
      <translation>用于模拟测量的模型所保存的时间点。</translation>
    </message>
    <message>
      <source>Time step</source>
      <translation>时间步</translation>
    </message>
    <message>
      <source>2  Survey line</source>
      <translation>2  测线</translation>
    </message>
    <message>
      <source>Start</source>
      <translation>开始</translation>
    </message>
    <message>
      <source>End</source>
      <translation>终点</translation>
    </message>
    <message>
      <source>Clear line</source>
      <translation>清除测线</translation>
    </message>
    <message>
      <source>Points along the line</source>
      <translation>沿测线的点</translation>
    </message>
    <message>
      <source>3  Surveys</source>
      <translation>3  测量</translation>
    </message>
    <message>
      <source>Tick the surveys to simulate along the line. Each starts on settings that work; unfold a line to change them.</source>
      <translation>勾选要沿测线模拟的测量。每项均以可用的设置开始；展开一行即可修改。</translation>
    </message>
    <message>
      <source>Stations (EM, gravity)</source>
      <translation>测点（EM、重力）</translation>
    </message>
    <message>
      <source>Electrodes and array</source>
      <translation>电极与装置</translation>
    </message>
    <message>
      <source>Electrodes</source>
      <translation>电极</translation>
    </message>
    <message>
      <source>Spacing</source>
      <translation>间距</translation>
    </message>
    <message>
      <source>First electrode at</source>
      <translation>首电极位于</translation>
    </message>
    <message>
      <source>Array</source>
      <translation>装置</translation>
    </message>
    <message>
      <source>Added noise</source>
      <translation>添加噪声</translation>
    </message>
    <message>
      <source>Rock physics and errors</source>
      <translation>岩石物理与误差</translation>
    </message>
    <message>
      <source>The error each simulated reading is given, as a share of the reading, plus the absolute part.</source>
      <translation>赋予每个模拟读数的误差：按读数比例的部分加上绝对部分。</translation>
    </message>
    <message>
      <source>Error model</source>
      <extracomment>The "Fit to" choice changed: ``ert_records.FIT_ALL`` or ``FIT_KEPT``. "Use for the data errors" was pressed; the page sets its Data errors.</extracomment>
      <translation>误差模型</translation>
    </message>
    <message>
      <source>Geophones and shots</source>
      <translation>检波器与炮点</translation>
    </message>
    <message>
      <source>Geophones</source>
      <translation>检波器</translation>
    </message>
    <message>
      <source>First geophone at</source>
      <translation>首检波器位于</translation>
    </message>
    <message>
      <source>A shot every</source>
      <translation>炮间隔</translation>
    </message>
    <message>
      <source>Regolith pressure depth</source>
      <translation>风化层压力深度</translation>
    </message>
    <message>
      <source>Crack aspect ratio</source>
      <translation>裂隙纵横比</translation>
    </message>
    <message>
      <source>Absolute noise</source>
      <translation>绝对噪声</translation>
    </message>
    <message>
      <source>Pore-water conductivity</source>
      <translation>孔隙水电导率</translation>
    </message>
    <message>
      <source>Cementation exponent m</source>
      <translation>胶结指数 m</translation>
    </message>
    <message>
      <source>Saturation exponent n</source>
      <translation>饱和度指数 n</translation>
    </message>
    <message>
      <source>Surface conductivity</source>
      <translation>表面电导率</translation>
    </message>
    <message>
      <source>Time gates</source>
      <translation>时窗</translation>
    </message>
    <message>
      <source>Times</source>
      <translation>时间</translation>
    </message>
    <message>
      <source>Rock physics and loop</source>
      <translation>岩石物理与回线</translation>
    </message>
    <message>
      <source>Loop radius</source>
      <translation>回线半径</translation>
    </message>
    <message>
      <source>Frequencies</source>
      <translation>频率</translation>
    </message>
    <message>
      <source>How many</source>
      <translation>数量</translation>
    </message>
    <message>
      <source>Rock physics and instrument</source>
      <translation>岩石物理与仪器</translation>
    </message>
    <message>
      <source>Transmitter at</source>
      <translation>发射位于</translation>
    </message>
    <message>
      <source>Receiver at</source>
      <translation>接收位置</translation>
    </message>
    <message>
      <source>Receiver orientation</source>
      <translation>接收方向</translation>
    </message>
    <message>
      <source>Receiver component</source>
      <translation>接收分量</translation>
    </message>
    <message>
      <source>Sensor</source>
      <translation>传感器</translation>
    </message>
    <message>
      <source>Height above ground</source>
      <translation>离地高度</translation>
    </message>
    <message>
      <source>Densities and model grid</source>
      <translation>密度与模型网格</translation>
    </message>
    <message>
      <source>Grain density</source>
      <translation>颗粒密度</translation>
    </message>
    <message>
      <source>Water density</source>
      <translation>水密度</translation>
    </message>
    <message>
      <source>Air density</source>
      <translation>空气密度</translation>
    </message>
    <message>
      <source>Grid cells</source>
      <translation>网格单元</translation>
    </message>
    <message>
      <source>Model width</source>
      <translation>模型宽度</translation>
    </message>
    <message>
      <source>Simulation</source>
      <translation>模拟</translation>
    </message>
    <message>
      <source>Rarely needs changing.</source>
      <translation>通常无需更改。</translation>
    </message>
    <message>
      <source>Noise seed, mesh and saved settings</source>
      <translation>噪声种子、网格和已保存的设置</translation>
    </message>
    <message>
      <source>Noise seed</source>
      <translation>噪声种子</translation>
    </message>
    <message>
      <source>Mesh quality</source>
      <translation>网格质量</translation>
    </message>
    <message>
      <source>Largest mesh cell</source>
      <translation>最大网格单元</translation>
    </message>
    <message>
      <source>Save survey settings</source>
      <translation>保存测量设置</translation>
    </message>
    <message>
      <source>Write the line, the surveys and their settings to survey_config.json, without simulating anything.</source>
      <translation>将测线、各期测量及其设置写入 survey_config.json，不进行任何模拟。</translation>
    </message>
    <message>
      <source>{0} electrodes {1:g} m apart, {2} array, {3:g} % noise.</source>
      <translation>{0} 个电极，间距 {1:g} m，{2}装置，{3:g} % 噪声。</translation>
    </message>
    <message>
      <source>{0} geophones {1:g} m apart, a shot every {2}, {3:g} % noise.</source>
      <translation>{0} 个检波器，间距 {1:g} m，每 {2} 一炮，{3:g} % 噪声。</translation>
    </message>
    <message>
      <source>{0} time gates from {1:g} to {2:g} ms, {3:g} % noise.</source>
      <translation>{0} 个时窗，{1:g} 至 {2:g} ms，{3:g} % 噪声。</translation>
    </message>
    <message>
      <source>{0} frequencies from {1:g} to {2:g} Hz, {3:g} % noise.</source>
      <translation>{0} 个频率，{1:g} 至 {2:g} Hz，{3:g} % 噪声。</translation>
    </message>
    <message>
      <source>Sensor {0:g} m above the ground, {1:g} % noise.</source>
      <translation>传感器离地 {0:g} m，噪声 {1:g} %。</translation>
    </message>
    <message>
      <source>The spread is {0:.0f} m, longer than the {1:.0f} m line: use fewer or closer {2}.</source>
      <translation>排列长度为 {0:.0f} m，超过 {1:.0f} m 的测线：请减少 {2} 数量或缩小其间距。</translation>
    </message>
    <message>
      <source>Hydro input data format</source>
      <translation>水文输入数据格式</translation>
    </message>
    <message>
      <source>Select hydro data folder</source>
      <translation>选择水文数据文件夹</translation>
    </message>
    <message>
      <source>No model loaded. Open a folder with Watercontent.npy, Porosity.npy, top.npy and bot.npy, or use the example.</source>
      <translation>未载入模型。请打开包含 Watercontent.npy、Porosity.npy、top.npy 和 bot.npy 的文件夹，或使用示例。</translation>
    </message>
    <message>
      <source>(one time)</source>
      <translation>（单一时刻）</translation>
    </message>
    <message>
      <source>Line from ({0:.0f}, {1:.0f}) to ({2:.0f}, {3:.0f}), about {4:.0f} m. The Section tab shows the ground under it.</source>
      <translation>测线从 ({0:.0f}, {1:.0f}) 至 ({2:.0f}, {3:.0f})，约 {4:.0f} m。“断面”选项卡显示其下方的地下情况。</translation>
    </message>
    <message>
      <source>{0} under the line, time step {1}</source>
      <translation>测线下方的{0}，时间步 {1}</translation>
    </message>
    <message>
      <source>Nothing was simulated; the survey settings were saved instead.</source>
      <translation>未进行模拟；已改为保存勘探设置。</translation>
    </message>
    <message>
      <source>Simulated {0} on the line. Each method's model and synthetic data are shown below.</source>
      <translation>已在测线上模拟 {0}。各方法的模型和合成数据显示如下。</translation>
    </message>
    <message>
      <source>No {0} figure for this method.</source>
      <translation>此方法没有 {0} 图件。</translation>
    </message>
    <message>
      <source>Simulating…</source>
      <translation>正在模拟…</translation>
    </message>
    <message>
      <source>Starting the simulation…</source>
      <translation>正在启动模拟…</translation>
    </message>
    <message>
      <source>Finished. The results are on the Results tab.</source>
      <translation>已完成。结果位于“结果”选项卡。</translation>
    </message>
    <message>
      <source>The simulation failed: {0}</source>
      <translation>模拟失败：{0}</translation>
    </message>
    <message>
      <source>Stopped before it finished. Press Simulate surveys to start again.</source>
      <translation>未完成即已停止。按“模拟测量”重新开始。</translation>
    </message>
    <message>
      <source>Back</source>
      <translation>返回</translation>
    </message>
    <message>
      <source>Next</source>
      <translation>下一步</translation>
    </message>
    <message>
      <source>&lt;h3&gt;Step 1 · Select two geophysical methods&lt;/h3&gt;</source>
      <translation>&lt;h3&gt;第 1 步 · 选择两种地球物理方法&lt;/h3&gt;</translation>
    </message>
    <message>
      <source>The compatibility registry distinguishes simultaneous joint inversion from cooperative/sequential constraints. Planned combinations are visible but cannot run.</source>
      <translation>兼容性注册表区分同步联合反演与协同/顺序约束。计划中的组合可见，但无法运行。</translation>
    </message>
    <message>
      <source>Method A</source>
      <translation>方法 A</translation>
    </message>
    <message>
      <source>Method B</source>
      <translation>方法 B</translation>
    </message>
    <message>
      <source>Joint strategy</source>
      <translation>联合策略</translation>
    </message>
    <message>
      <source>&lt;span style='color:{0}'&gt;&lt;b&gt;Unavailable:&lt;/b&gt; {1}&lt;/span&gt;</source>
      <translation>&lt;span style='color:{0}'&gt;&lt;b&gt;不可用：&lt;/b&gt;{1}&lt;/span&gt;</translation>
    </message>
    <message>
      <source>&lt;span style='color:{0}'&gt;&lt;b&gt;Available&lt;/b&gt;&lt;/span&gt; · {1} · {2} · backend: {3}&lt;br&gt;{4}</source>
      <translation>&lt;span style='color:{0}'&gt;&lt;b&gt;可用&lt;/b&gt;&lt;/span&gt; · {1} · {2} · 后端：{3}&lt;br&gt;{4}</translation>
    </message>
    <message>
      <source>&lt;span style='color:{0}'&gt;&lt;b&gt;Backend unavailable:&lt;/b&gt; {1}&lt;/span&gt;</source>
      <translation>&lt;span style='color:{0}'&gt;&lt;b&gt;后端不可用：&lt;/b&gt;{1}&lt;/span&gt;</translation>
    </message>
    <message>
      <source>&lt;span style='color:{0}'&gt;&lt;b&gt;Planned:&lt;/b&gt; no scientifically validated joint runner is registered for this pair.&lt;/span&gt;</source>
      <translation>&lt;span style='color:{0}'&gt;&lt;b&gt;计划中：&lt;/b&gt;该方法组合尚未注册经过科学验证的联合反演程序。&lt;/span&gt;</translation>
    </message>
    <message>
      <source>&lt;h3&gt;Step 2 · Load or reuse observed data&lt;/h3&gt;</source>
      <translation>&lt;h3&gt;第 2 步 · 载入或复用观测数据&lt;/h3&gt;</translation>
    </message>
    <message>
      <source>Joint inversion always requires observations. Existing recovered models may be used later as starting/reference models, but never replace observed data.</source>
      <translation>联合反演始终需要观测数据。已有的反演模型之后可用作初始/参考模型，但不能替代观测数据。</translation>
    </message>
    <message>
      <source>Upload file…</source>
      <translation>上传文件…</translation>
    </message>
    <message>
      <source>Use bundled example for selected pair</source>
      <translation>为所选组合使用内置示例</translation>
    </message>
    <message>
      <source>{0} observations</source>
      <translation>{0} 个观测值</translation>
    </message>
    <message>
      <source>Choose a project resource or upload a file</source>
      <translation>选择工程资源或上传文件</translation>
    </message>
    <message>
      <source>Load {0} observations</source>
      <translation>载入 {0} 观测数据</translation>
    </message>
    <message>
      <source>&lt;h3&gt;Step 3 · Check geometry and model compatibility&lt;/h3&gt;</source>
      <translation>&lt;h3&gt;第 3 步 · 检查几何与模型兼容性&lt;/h3&gt;</translation>
    </message>
    <message>
      <source>Explicit profile-coordinate offsets (ERT + SRT only)</source>
      <translation>显式指定剖面坐标偏移（仅 ERT + SRT）</translation>
    </message>
    <message>
      <source>ERT x offset (m)</source>
      <translation>ERT x 偏移 (m)</translation>
    </message>
    <message>
      <source>ERT z offset (m)</source>
      <translation>ERT z 偏移 (m)</translation>
    </message>
    <message>
      <source>SRT x offset (m)</source>
      <translation>SRT x 偏移 (m)</translation>
    </message>
    <message>
      <source>SRT z offset (m)</source>
      <translation>SRT z 偏移 (m)</translation>
    </message>
    <message>
      <source>Explicit EM sounding pairing</source>
      <translation>显式指定 EM 测深配对</translation>
    </message>
    <message>
      <source>Load pairing CSV…</source>
      <translation>载入配对 CSV…</translation>
    </message>
    <message>
      <source>No pairing table loaded.</source>
      <translation>未载入配对表。</translation>
    </message>
    <message>
      <source>Validate compatibility</source>
      <translation>验证兼容性</translation>
    </message>
    <message>
      <source>Offsets are never inferred or applied automatically. Confirm that both sensor arrays belong to the same profile before validation.</source>
      <translation>偏移量不会被自动推断或应用。验证前请确认两组传感器排列属于同一剖面。</translation>
    </message>
    <message>
      <source>Soundings</source>
      <translation>测深</translation>
    </message>
    <message>
      <source>With coordinates, soundings are matched one-to-one by distance. Without coordinates, equal-sized lines are paired by index; unequal counts require a pairing table.</source>
      <translation>有坐标时，测深点按距离一一匹配。无坐标时，点数相同的测线按序号配对；点数不同则需要配对表。</translation>
    </message>
    <message>
      <source>Both surveys must use the same projected coordinate system and overlap in x and y. The workflow does not infer a reprojection or coordinate offset.</source>
      <translation>两次测量必须使用相同的投影坐标系，且在 x 和 y 上重叠。工作流不会推断重投影或坐标偏移。</translation>
    </message>
    <message>
      <source>Load FDEM/TDEM pairing table</source>
      <translation>载入 FDEM/TDEM 配对表</translation>
    </message>
    <message>
      <source>{0} · {1} pair(s)</source>
      <translation>{0} · {1} 对</translation>
    </message>
    <message>
      <source>&lt;h3&gt;Step 4 · Choose a preset and tune joint parameters&lt;/h3&gt;</source>
      <translation>&lt;h3&gt;第 4 步 · 选择预设并调整联合参数&lt;/h3&gt;</translation>
    </message>
    <message>
      <source>Run independent single-method inversions for comparison</source>
      <translation>运行独立的单方法反演以作对比</translation>
    </message>
    <message>
      <source>Maximum iterations</source>
      <translation>最大迭代次数</translation>
    </message>
    <message>
      <source>Baseline comparison</source>
      <translation>基准对比</translation>
    </message>
    <message>
      <source>Advanced</source>
      <translation>高级</translation>
    </message>
    <message>
      <source>Use current project seismic interface when available</source>
      <translation>如有，使用当前工程的地震界面</translation>
    </message>
    <message>
      <source>Auto (SimPEG native, SciPy fallback)</source>
      <translation>自动（SimPEG 原生，SciPy 备用）</translation>
    </message>
    <message>
      <source>SimPEG native</source>
      <translation>SimPEG 原生</translation>
    </message>
    <message>
      <source>SciPy fallback</source>
      <translation>SciPy 后备方案</translation>
    </message>
    <message>
      <source>Auto uses native SimPEG joint inversion when SimPEG &gt;= 0.25.2 is available.</source>
      <translation>当 SimPEG &gt;= 0.25.2 可用时，自动模式使用 SimPEG 原生联合反演。</translation>
    </message>
    <message>
      <source>&lt;h3&gt;Step 5 · Review and run&lt;/h3&gt;</source>
      <translation>&lt;h3&gt;第 5 步 · 检查并运行&lt;/h3&gt;</translation>
    </message>
    <message>
      <source>Ready.</source>
      <translation>就绪。</translation>
    </message>
    <message>
      <source>Stopped by user.</source>
      <translation>已由用户停止。</translation>
    </message>
    <message>
      <source>Run joint inversion</source>
      <translation>运行联合反演</translation>
    </message>
    <message>
      <source>Starting joint inversion…</source>
      <translation>正在启动联合反演…</translation>
    </message>
    <message>
      <source>Failed: {0}</source>
      <translation>失败：{0}</translation>
    </message>
    <message>
      <source>&lt;h3&gt;Step 6 · Joint inversion results&lt;/h3&gt;</source>
      <translation>&lt;h3&gt;第 6 步 · 联合反演结果&lt;/h3&gt;</translation>
    </message>
    <message>
      <source>Export models as CSV…</source>
      <translation>将模型导出为 CSV…</translation>
    </message>
    <message>
      <source>Write one table per method that carries its own coordinates, so the models can be replotted without PyGIMLi or SimPEG.</source>
      <translation>为每种方法写出一个自带坐标的表格，以便无需 PyGIMLi 或 SimPEG 即可重新绘制模型。</translation>
    </message>
    <message>
      <source>Overview</source>
      <translation>概览</translation>
    </message>
    <message>
      <source>Models</source>
      <translation>模型</translation>
    </message>
    <message>
      <source>Data Fit</source>
      <translation>数据拟合</translation>
    </message>
    <message>
      <source>Baseline Comparison</source>
      <translation>基准对比</translation>
    </message>
    <message>
      <source>Files</source>
      <translation>文件</translation>
    </message>
    <message>
      <source>Sequential structural constraint</source>
      <extracomment>The quantity each joint model is, as (colormap key, the map the Models tab has always drawn it with): PyGIMLi's own viridis for the ERT and SRT sections, RdBu_r for density contrast and viridis otherwise. The keys are the ones those quantities have on their own pages, so a map chosen for resistivity sections on the ERT page is the one used here too. The model each panel's colour range was last set for.</extracomment>
      <translation>顺序结构约束</translation>
    </message>
    <message>
      <source>Cell index</source>
      <translation>单元索引</translation>
    </message>
    <message>
      <source>{0} joint model</source>
      <translation>{0} 联合模型</translation>
    </message>
    <message>
      <source>{0} · middle-y slice</source>
      <translation>{0} · y 中间切片</translation>
    </message>
    <message>
      <source>Resistivity (Ω m)</source>
      <translation>电阻率 (Ω m)</translation>
    </message>
    <message>
      <source>Matched sounding</source>
      <translation>匹配的测深</translation>
    </message>
    <message>
      <source>Layer</source>
      <translation>层</translation>
    </message>
    <message>
      <source>Shared FDEM–TDEM resistivity model</source>
      <translation>FDEM–TDEM 共享电阻率模型</translation>
    </message>
    <message>
      <source>{0} data fit</source>
      <translation>{0} 数据拟合</translation>
    </message>
    <message>
      <source>Datum</source>
      <translation>基准面</translation>
    </message>
    <message>
      <source>Layer / cell</source>
      <translation>层 / 单元</translation>
    </message>
    <message>
      <source>Export joint models to folder</source>
      <translation>导出联合模型到文件夹</translation>
    </message>
    <message>
      <source>3D preview unavailable:&lt;br&gt;&lt;code&gt;{0}&lt;/code&gt;&lt;br&gt;&lt;br&gt;{1}</source>
      <extracomment>The ERT page's key in the studio, which a mesh built here can be handed to. A note under a row, and one that warns. What the E4D engine lays its mesh out from while no .cfg is loaded.</extracomment>
      <translation>3D 预览不可用：&lt;br&gt;&lt;code&gt;{0}&lt;/code&gt;&lt;br&gt;&lt;br&gt;{1}</translation>
    </message>
    <message>
      <source>Outer region</source>
      <translation>外部区域</translation>
    </message>
    <message>
      <source>Show the coarse outer region (marker 1) too. Off, the view keeps to the cells an inversion solves for, around the sensors.</source>
      <translation>同时显示粗糙外围区域（标记 1）。关闭时，视图仅显示电极周围参与反演求解的单元。</translation>
    </message>
    <message>
      <source>Colour map</source>
      <translation>色标</translation>
    </message>
    <message>
      <source>1. Sensor array</source>
      <translation>1. 电极排列</translation>
    </message>
    <message>
      <source>Build mesh from sensor file…</source>
      <translation>由电极文件构建网格…</translation>
    </message>
    <message>
      <source>Pick a CSV or text table of sensor positions (x, y, z in metres, such as Cable,Elec,X,Y,Z) and generate the mesh under them straight away, with the settings of the steps below. To change the settings first, choose {0} as the array and load the file there.</source>
      <translation>选择包含电极位置的 CSV 或文本表（x、y、z，单位为米，例如 Cable,Elec,X,Y,Z），并立即按下面各步骤的设置在其下方生成网格。如需先修改设置，请选择 {0} 作为装置并在其中载入该文件。</translation>
    </message>
    <message>
      <source>Where the electrodes, geophones or other sensors are: a grid on the surface, one borehole, several boreholes, a line on the surface beside a borehole, or the positions a file lists.</source>
      <translation>电极、检波器或其他传感器的位置：地表网格、单个钻孔、多个钻孔、钻孔旁的地表测线，或文件中列出的位置。</translation>
    </message>
    <message>
      <source>Load sensor file…</source>
      <translation>载入电极文件…</translation>
    </message>
    <message>
      <source>A table of sensor positions, CSV or text: x, y and z in metres, such as Cable,Elec,X,Y,Z. The header says which column is which; without one, a sensor-number column is set aside. A table of x and z alone is a line at y = 0.</source>
      <translation>电极位置表，CSV 或文本格式：x、y、z（单位 m），例如 Cable,Elec,X,Y,Z。表头指明各列含义；若无表头，电极编号列将被忽略。仅含 x 和 z 的表视为 y = 0 的测线。</translation>
    </message>
    <message>
      <source>No file loaded.</source>
      <translation>未载入文件。</translation>
    </message>
    <message>
      <source>Elevation of the top sensor; the rest are spaced evenly down to the bottom one.</source>
      <translation>最上方电极的高程；其余电极向下等间距排布至最下方电极。</translation>
    </message>
    <message>
      <source>2. Mesh engine</source>
      <translation>2. 网格引擎</translation>
    </message>
    <message>
      <source>Auto: prism for surface+topography, structured otherwise.
Gmsh (tetrahedral): high-quality refined tet mesh (flat top; best for box / borehole / mild terrain).
PyGIMLi prism: topography-conforming.
Structured grid: fast regular grid.
E4D (Triangle + TetGen): a fine zone around the electrodes inside a coarse outer zone reaching far out, written as an E4D .cfg that E4D itself runs on.</source>
      <translation>自动：地表+地形时使用棱柱网格，否则使用结构化网格。
Gmsh（四面体）：高质量加密四面体网格（顶面平坦；最适合箱体/钻孔/缓地形）。
PyGIMLi 棱柱：贴合地形。
结构化网格：快速规则网格。
E4D（Triangle + TetGen）：电极周围的精细区域位于向外远延的粗外部区域内，写为 E4D .cfg，由 E4D 自身运行。</translation>
    </message>
    <message>
      <source>Load E4D .cfg…</source>
      <translation>载入 E4D .cfg…</translation>
    </message>
    <message>
      <source>Build from an existing E4D mesh configuration file instead of the sensor array, domain and refinement set here.</source>
      <translation>使用现有的 E4D 网格配置文件构建，而不使用此处设置的电极排列、计算域和加密参数。</translation>
    </message>
    <message>
      <source>Go back to building from steps 1, 3 and 4.</source>
      <translation>恢复为按步骤 1、3 和 4 构建。</translation>
    </message>
    <message>
      <source>TetGen is what E4D runs: the program if it is on PATH, otherwise its Python package (pip install tetgen). Gmsh stands in when TetGen is not installed; it aims at the zone volumes rather than enforcing them, so the log reports each zone's largest element against its limit.</source>
      <translation>E4D 使用 TetGen：若 PATH 中有该程序则使用程序，否则使用其 Python 包（pip install tetgen）。未安装 TetGen 时由 Gmsh 替代；Gmsh 只以分区体积为目标而不强制执行，因此日志会报告每个分区的最大单元及其限值。</translation>
    </message>
    <message>
      <source>TetGen program (optional)</source>
      <translation>TetGen 程序（可选）</translation>
    </message>
    <message>
      <source>Path to a TetGen executable, when it is neither on PATH nor installed as the Python package.</source>
      <translation>TetGen 可执行文件的路径，用于其既不在 PATH 中、也未作为 Python 包安装的情况。</translation>
    </message>
    <message>
      <source>The zones' starting conductivity, written into the E4D configuration.</source>
      <translation>各分区的初始电导率，写入 E4D 配置。</translation>
    </message>
    <message>
      <source>Single region (one marker)</source>
      <translation>单一区域（一个标记）</translation>
    </message>
    <message>
      <source>Collapse the mesh to one marker instead of preserving the parameter-domain (2) / boundary (1) split.</source>
      <translation>将网格合并为单一标记，而不保留参数域 (2) / 边界 (1) 的划分。</translation>
    </message>
    <message>
      <source>3. Domain and topography</source>
      <translation>3. 计算域与地形</translation>
    </message>
    <message>
      <source>Surface with topography builds the domain around the sensors, under the ground set below. Box mesh builds a box of the size set below, from the origin.</source>
      <translation>“带地形的地表”围绕电极、在下方设定的地面以下构建计算域。“箱体网格”从原点起构建下方设定尺寸的箱体。</translation>
    </message>
    <message>
      <source>Domain</source>
      <translation>计算域</translation>
    </message>
    <message>
      <source>Depth of the inverted region (marker 2) below the top of the mesh; the cells below it are the outer region (marker 1), and zones act only above it. Under a surface grid it is also how deep the mesh reaches.</source>
      <translation>反演区域（标记 2）在网格顶部以下的深度；其下方的单元为外部区域（标记 1），分区仅在其上方起作用。使用地表网格时，它也是网格延伸的深度。</translation>
    </message>
    <message>
      <source>How far the domain reaches beyond a surface grid, as a multiple of the grid's size: 1.4 adds a fifth of its length on each side.</source>
      <translation>计算区域超出地表网格的范围，以网格尺寸的倍数表示：1.4 表示每侧各增加其长度的五分之一。</translation>
    </message>
    <message>
      <source>A coarse region (marker 1, not inverted) reaching this many times the domain's larger side beyond it, sideways and down, as on the ERT page's own mesh: it carries the far boundary away from the sensors. 0 leaves it out; a box mesh has none, its walls being the tank's.</source>
      <translation>粗网格区域（标记 1，不参与反演），向两侧及下方延伸至计算域较长边的该倍数，与 ERT 页面自身的网格相同：用于将远边界推离电极。设为 0 则不添加；箱体网格没有该区域，其边壁即为水槽壁。</translation>
    </message>
    <message>
      <source>How far the domain reaches beyond the outermost boreholes, in x and y.</source>
      <translation>计算区域在 x 和 y 方向超出最外侧钻孔的距离。</translation>
    </message>
    <message>
      <source>How far the domain reaches above the highest sensor.</source>
      <translation>计算区域在最高电极以上延伸的距离。</translation>
    </message>
    <message>
      <source>How far the domain reaches below the deepest sensor - for Gmsh, below the investigation depth under it.</source>
      <translation>计算区域在最深电极以下延伸的距离；对于 Gmsh，为其下方探测深度以下的延伸距离。</translation>
    </message>
    <message>
      <source>How far the fine zone reaches beyond the outermost electrodes, in x and y.</source>
      <translation>精细区在 x 和 y 方向超出最外侧电极的距离。</translation>
    </message>
    <message>
      <source>How far the fine zone reaches below the deepest electrode.</source>
      <translation>精细区在最深电极以下延伸的距离。</translation>
    </message>
    <message>
      <source>How far beyond the fine zone the outer boundary sits. The potentials must have died away there; ten times the survey size is the usual rule.</source>
      <translation>外边界距精细区的距离。边界处的电位必须已衰减殆尽；通常取测区尺寸的十倍。</translation>
    </message>
    <message>
      <source>Depth of the mesh bottom below the lowest point of the surface (E4D's m_bot).</source>
      <translation>网格底部在地表最低点以下的深度（E4D 的 m_bot）。</translation>
    </message>
    <message>
      <source>The ground surface: what the mesh is built under, and what the sensors of a surface grid are placed on.</source>
      <translation>地面：网格在其下方构建，地表网格的电极也布设在其上。</translation>
    </message>
    <message>
      <source>Topography</source>
      <translation>地形</translation>
    </message>
    <message>
      <source>z = f(x, y). Allowed: x, y, np, sin, cos, exp, sqrt, abs, pi.</source>
      <translation>z = f(x, y)。允许使用：x, y, np, sin, cos, exp, sqrt, abs, pi。</translation>
    </message>
    <message>
      <source>Load topography file (x, y, z)…</source>
      <translation>载入地形文件 (x, y, z)…</translation>
    </message>
    <message>
      <source>No file loaded. The surface is interpolated from the points.</source>
      <translation>未载入文件。曲面将由点插值生成。</translation>
    </message>
    <message>
      <source>Load sensor positions</source>
      <translation>载入电极位置</translation>
    </message>
    <message>
      <source>Build a mesh from sensor positions</source>
      <translation>由电极位置构建网格</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0}&lt;/b&gt;: {1} sensors, {2}. x {3:g} to {4:g}, y {5:g} to {6:g}, z {7:g} to {8:g} m ({9}).</source>
      <translation>&lt;b&gt;{0}&lt;/b&gt;：{1} 个电极，{2}。x {3:g} 至 {4:g}，y {5:g} 至 {6:g}，z {7:g} 至 {8:g} m（{9}）。</translation>
    </message>
    <message>
      <source>Load topography points (x, y, z)</source>
      <translation>载入地形点 (x, y, z)</translation>
    </message>
    <message>
      <source>{0}: {1} points (z {2:.1f} to {3:.1f} m)</source>
      <translation>{0}：{1} 个点（z {2:.1f} 至 {3:.1f} m）</translation>
    </message>
    <message>
      <source>4. Mesh refinement</source>
      <translation>4. 网格加密</translation>
    </message>
    <message>
      <source>Gmsh: the element size at the sensors.</source>
      <translation>Gmsh：电极处的单元尺寸。</translation>
    </message>
    <message>
      <source>Gmsh: the distance from the sensors over which the elements grow from the sensor size to the boundary size.</source>
      <translation>Gmsh：单元尺寸从电极处尺寸增长到边界尺寸所跨越的、距电极的距离。</translation>
    </message>
    <message>
      <source>Gmsh: the element size away from the sensors. The structured grid under a surface grid: its horizontal cell size.</source>
      <translation>Gmsh：远离电极处的单元尺寸。对于地表网格下方的结构化网格：为其水平单元尺寸。</translation>
    </message>
    <message>
      <source>The prism mesh: the thickness of its fine layers. The structured grid under a surface grid: its vertical cell size.</source>
      <translation>棱柱网格：细层的厚度。地表网格下方的结构化网格：其垂向单元尺寸。</translation>
    </message>
    <message>
      <source>The prism mesh: the thickness of its coarse layers.</source>
      <translation>棱柱网格：粗层的厚度。</translation>
    </message>
    <message>
      <source>The structured grid around boreholes: its horizontal cell size.</source>
      <translation>钻孔周围的结构化网格：其水平单元尺寸。</translation>
    </message>
    <message>
      <source>The structured grid around boreholes: its vertical cell size.</source>
      <translation>钻孔周围的结构化网格：其垂向单元尺寸。</translation>
    </message>
    <message>
      <source>The largest element allowed in the fine zone - E4D's zone volume. Halving it roughly doubles the elements there.</source>
      <translation>精细区允许的最大单元，即 E4D 的分区体积。减半大约会使该区单元数翻倍。</translation>
    </message>
    <message>
      <source>Largest radius-edge ratio of any element (TetGen -q). Lower is better shaped and costs more elements; the E4D guide recommends 1.3 to 1.5.</source>
      <translation>任一单元的最大半径-边长比（TetGen -q）。数值越小单元形状越好，但单元数越多；E4D 指南建议取 1.3 至 1.5。</translation>
    </message>
    <message>
      <source>Offset of the refinement point placed beside each buried electrode (and under each borehole top), which forces small elements where the potential changes fastest. 0 adds none.</source>
      <translation>在每个埋设电极旁（以及每个钻孔顶部下方）放置的加密点的偏移距离，用于在电位变化最快处强制生成小单元。0 表示不添加。</translation>
    </message>
    <message>
      <source>5. Zones (optional)</source>
      <translation>5. 分区（可选）</translation>
    </message>
    <message>
      <source>6. Build and save</source>
      <translation>6. 生成并保存</translation>
    </message>
    <message>
      <source>The name of the saved files, before the extension.</source>
      <translation>保存文件的名称（不含扩展名）。</translation>
    </message>
    <message>
      <source>Mesh name</source>
      <translation>网格名称</translation>
    </message>
    <message>
      <source>BMS</source>
      <translation>BMS</translation>
    </message>
    <message>
      <source>VTK</source>
      <translation>VTK</translation>
    </message>
    <message>
      <source>Sensor CSV</source>
      <translation>传感器 CSV</translation>
    </message>
    <message>
      <source>Save as</source>
      <translation>另存为</translation>
    </message>
    <message>
      <source>Mesh files are saved under the active Project's unique run directory.</source>
      <translation>网格文件保存在当前工程的唯一运行目录下。</translation>
    </message>
    <message>
      <source>Open</source>
      <translation>打开</translation>
    </message>
    <message>
      <source>Open the folder the last build saved to.</source>
      <translation>打开上次构建所保存到的文件夹。</translation>
    </message>
    <message>
      <source>Folder</source>
      <translation>文件夹</translation>
    </message>
    <message>
      <source>Preview sensors</source>
      <translation>预览电极</translation>
    </message>
    <message>
      <source>Draw the sensors, the ground and the zones - with the E4D engine its whole layout - before anything is meshed.</source>
      <translation>在剖分网格之前绘制电极、地面和分区（使用 E4D 引擎时绘制其完整布局）。</translation>
    </message>
    <message>
      <source>Generate mesh</source>
      <translation>生成网格</translation>
    </message>
    <message>
      <source>Use for ERT inversion</source>
      <translation>用于 ERT 反演</translation>
    </message>
    <message>
      <source>Open the ERT page with this mesh as the mesh its inversion runs on. The page checks that the mesh holds the loaded survey's electrodes, and shows it on its Mesh tab.</source>
      <translation>打开 ERT 页面，并以此网格作为其反演所用的网格。该页面会检查网格是否包含已载入勘探的电极，并在其“网格”选项卡中显示该网格。</translation>
    </message>
    <message>
      <source>Work down the steps, preview the layout, then generate the mesh.</source>
      <translation>按步骤依次进行，预览布局，然后生成网格。</translation>
    </message>
    <message>
      <source>Not used: {0} sets the electrodes. Clear it in step 2 (✕) to build from this array.</source>
      <translation>不使用：电极由 {0} 设定。在第 2 步中将其清除（✕）即可按此装置构建。</translation>
    </message>
    <message>
      <source>Preview E4D layout</source>
      <translation>预览 E4D 布局</translation>
    </message>
    <message>
      <source>Output directory</source>
      <translation>输出目录</translation>
    </message>
    <message>
      <source>Preview failed: {0}</source>
      <translation>预览失败：{0}</translation>
    </message>
    <message>
      <source>{0} sensors  ·  x [{1:.1f}, {2:.1f}]  y [{3:.1f}, {4:.1f}]  z [{5:.2f}, {6:.2f}] m</source>
      <translation>{0} 个传感器  ·  x [{1:.1f}, {2:.1f}]  y [{3:.1f}, {4:.1f}]  z [{5:.2f}, {6:.2f}] m</translation>
    </message>
    <message>
      <source>Load E4D mesh configuration</source>
      <translation>载入 E4D 网格配置</translation>
    </message>
    <message>
      <source>Open E4D mesh</source>
      <translation>打开 E4D 网格</translation>
    </message>
    <message>
      <source>Reading {0}…</source>
      <translation>正在读取 {0}…</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0}&lt;/b&gt;: {1} cells, {2} nodes ({3}){4}</source>
      <translation>&lt;b&gt;{0}&lt;/b&gt;：{1} 个单元，{2} 个节点（{3}）{4}</translation>
    </message>
    <message>
      <source>Load a sensor file in step 1 first.</source>
      <translation>请先在第 1 步中载入电极文件。</translation>
    </message>
    <message>
      <source>Generating…</source>
      <translation>正在生成…</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0}&lt;/b&gt;&lt;br&gt;cells: {1}  ·  nodes: {2}  ·  {3}: {4}{5}{6}</source>
      <translation>&lt;b&gt;{0}&lt;/b&gt;&lt;br&gt;单元：{1}  ·  节点：{2}  ·  {3}：{4}{5}{6}</translation>
    </message>
    <message>
      <source>Generation failed: {0}</source>
      <translation>生成失败：{0}</translation>
    </message>
    <message>
      <source>Stopped before the mesh was finished. Generate it again to start over.</source>
      <translation>网格未完成即已停止。重新生成以从头开始。</translation>
    </message>
    <message>
      <source>3D ERT forward failed: {0}</source>
      <translation>3D ERT 正演失败：{0}</translation>
    </message>
    <message>
      <source>The 3D ERT forward model was stopped before it finished.</source>
      <translation>三维 ERT 正演未完成即已停止。</translation>
    </message>
    <message>
      <source>Load mesh</source>
      <translation>载入网格</translation>
    </message>
    <message>
      <source>3D viewer unavailable. File ready at:&lt;br&gt;&lt;code&gt;{0}&lt;/code&gt;</source>
      <translation>3D 查看器不可用。文件已就绪：&lt;br&gt;&lt;code&gt;{0}&lt;/code&gt;</translation>
    </message>
    <message>
      <source>Name this run</source>
      <extracomment>Symbol, colour and wording per Result Store status. A run list is scanned, not read, so the outcome has to survive peripheral vision. Metrics worth putting in the run summary before the raw record. ``smoothing_alpha`` is the weight R2 and R3t chose themselves, in place of lambda. Heading for runs this session produced that are not in the Project yet. What the Visualization tab's chooser leaves to Details in the compact view, and the run records it never offers there: a long series' per-survey QC logs are hundreds, listed on the Files tab instead. Beyond this a text record is shown from its end, where a log is read first.</extracomment>
      <translation>命名本次运行</translation>
    </message>
    <message>
      <source>Project: (not available)</source>
      <extracomment>Runs finished this session that are not in the Project's history yet.</extracomment>
      <translation>工程：（不可用）</translation>
    </message>
    <message>
      <source>Details</source>
      <translation>详情</translation>
    </message>
    <message>
      <source>Search runs…</source>
      <translation>搜索运行…</translation>
    </message>
    <message>
      <source>Status</source>
      <translation>状态</translation>
    </message>
    <message>
      <source>When</source>
      <translation>时间</translation>
    </message>
    <message>
      <source>Took</source>
      <translation>耗时</translation>
    </message>
    <message>
      <source>The name this run is listed under. It is kept when you press Enter or move on; F2 renames a run in the list too.</source>
      <translation>此运行在列表中显示的名称。按 Enter 或移到别处时保存；也可在列表中按 F2 重命名运行。</translation>
    </message>
    <message>
      <source>Size: —</source>
      <translation>大小：—</translation>
    </message>
    <message>
      <source>Save Notes</source>
      <translation>保存备注</translation>
    </message>
    <message>
      <source>Keep these notes with the run.</source>
      <translation>将这些备注与本次运行一同保存。</translation>
    </message>
    <message>
      <source>Save to Project</source>
      <translation>保存到工程</translation>
    </message>
    <message>
      <source>Add this run to the Project's history. Until then it exists only as a folder this session wrote, and closing the studio will ask.</source>
      <translation>将此次运行添加到工程历史记录。在此之前，它仅作为本会话写入的文件夹存在，关闭 Studio 时会询问。</translation>
    </message>
    <message>
      <source>Open Folder</source>
      <translation>打开文件夹</translation>
    </message>
    <message>
      <source>Open this run's folder in the system file manager.</source>
      <translation>在系统文件管理器中打开此次运行的文件夹。</translation>
    </message>
    <message>
      <source>Delete Run…</source>
      <translation>删除运行…</translation>
    </message>
    <message>
      <source>Notes</source>
      <translation>备注</translation>
    </message>
    <message>
      <source>Metric</source>
      <translation>指标</translation>
    </message>
    <message>
      <source>Run A</source>
      <translation>运行 A</translation>
    </message>
    <message>
      <source>Run B</source>
      <translation>运行 B</translation>
    </message>
    <message>
      <source>Difference</source>
      <translation>差值</translation>
    </message>
    <message>
      <source>Artifact:</source>
      <translation>产物：</translation>
    </message>
    <message>
      <source>Compare two models</source>
      <translation>比较两个模型</translation>
    </message>
    <message>
      <source>Select two runs with Ctrl-click, then compare aligned model grids.</source>
      <translation>按住 Ctrl 单击选择两个运行，然后比较对齐后的模型网格。</translation>
    </message>
    <message>
      <source>Kind</source>
      <translation>类型</translation>
    </message>
    <message>
      <source>Format</source>
      <translation>格式</translation>
    </message>
    <message>
      <source>Path</source>
      <translation>路径</translation>
    </message>
    <message>
      <source>Exists</source>
      <translation>已存在</translation>
    </message>
    <message>
      <source>Size</source>
      <translation>大小</translation>
    </message>
    <message>
      <source>Metrics</source>
      <translation>指标</translation>
    </message>
    <message>
      <source>Visualization</source>
      <translation>可视化</translation>
    </message>
    <message>
      <source>Report</source>
      <translation>报告</translation>
    </message>
    <message>
      <source>The convergence chart is unavailable in this environment.
Metric values are still listed above.</source>
      <translation>当前环境无法显示收敛图。
指标数值仍列在上方。</translation>
    </message>
    <message>
      <source>Browse Result Store</source>
      <translation>浏览结果库</translation>
    </message>
    <message>
      <source>Project: {0}{1}</source>
      <translation>工程：{0}{1}</translation>
    </message>
    <message>
      <source>None of the {0} recorded runs match the current search and status filter.</source>
      <translation>{0} 条已记录的运行均不符合当前的搜索和状态筛选条件。</translation>
    </message>
    <message>
      <source>Open folder</source>
      <translation>打开文件夹</translation>
    </message>
    <message>
      <source>{0} no longer exists:
{1}</source>
      <translation>{0} 已不存在：
{1}</translation>
    </message>
    <message>
      <source>Could not open {0}</source>
      <translation>无法打开 {0}</translation>
    </message>
    <message>
      <source>Rename…	F2</source>
      <translation>重命名…	F2</translation>
    </message>
    <message>
      <source>Open Run Folder</source>
      <translation>打开运行文件夹</translation>
    </message>
    <message>
      <source>Copy Folder Path</source>
      <translation>复制文件夹路径</translation>
    </message>
    <message>
      <source>Copy Run ID</source>
      <translation>复制运行 ID</translation>
    </message>
    <message>
      <source>Open Project Folder</source>
      <translation>打开工程文件夹</translation>
    </message>
    <message>
      <source>Refresh</source>
      <translation>刷新</translation>
    </message>
    <message>
      <source>Save notes</source>
      <translation>保存备注</translation>
    </message>
    <message>
      <source>Discard…</source>
      <translation>放弃…</translation>
    </message>
    <message>
      <source>This run was never added to the Project. Discarding deletes its folder.</source>
      <translation>此运行从未加入工程。丢弃将删除其文件夹。</translation>
    </message>
    <message>
      <source>Imported runs point at files this Project does not own.</source>
      <translation>导入的运行指向不属于本工程的文件。</translation>
    </message>
    <message>
      <source>A running computation cannot be deleted.</source>
      <translation>无法删除正在运行的计算。</translation>
    </message>
    <message>
      <source>Permanently delete this run's folder.</source>
      <translation>永久删除此次运行的文件夹。</translation>
    </message>
    <message>
      <source>Size: {0}</source>
      <translation>大小：{0}</translation>
    </message>
    <message>
      <source>Size: calculating…</source>
      <translation>大小：计算中…</translation>
    </message>
    <message>
      <source>Size: unavailable</source>
      <translation>大小：不可用</translation>
    </message>
    <message>
      <source>{0}
Double-click to open it.</source>
      <translation>{0}
双击打开。</translation>
    </message>
    <message>
      <source>Save run</source>
      <translation>保存运行</translation>
    </message>
    <message>
      <source>Save metadata</source>
      <translation>保存元数据</translation>
    </message>
    <message>
      <source>Discard unsaved run</source>
      <translation>放弃未保存的运行</translation>
    </message>
    <message>
      <source>Delete run permanently</source>
      <translation>永久删除运行</translation>
    </message>
    <message>
      <source>Delete run</source>
      <translation>删除运行</translation>
    </message>
    <message>
      <source>Step / slice:</source>
      <translation>步 / 切片：</translation>
    </message>
    <message>
      <source>The recording's streams, one per sample rate.</source>
      <extracomment>Periods (s) looked for as a receiver's own interference when a recording is read: Phoenix MTU-5C receivers can carry a pulse every 4 s of GPS time and a disturbance with every 30 s burst schedule. Share of a channel's full scale read as clipped: a decimated stream's filter rounds the flat top of a clipped stretch off a little below it. Most points a time-series panel draws across its width: a longer stretch is drawn as the range of each block of samples, and zooming in redraws it finer. A Directions box at this value keeps the direction the files give; one step up is north, and the arrows then step through east, south and west. The reader options each recording was read with: processing reads it again, from where it is, with the same ones. Interference found repeating on the receiver's clock: {period: [channel, ...]}. The grid frequency set on Power line because the recording held its hum. Each sample rate's runs as indices into ``self._runs``, one row of the Stream list per entry; the Run number picks within it, since a segmented recording has hundreds of bursts - too many for one list. What the Time series tab draws: its run, the channels' axes and traces, and the samples and block size the traces cover. Sites in list order: ``{"tf": TransferFunction, "source": Path | None}``. The Sites list, the 1D panel's site choice and the profile list all hold one row per entry, in this order.</extracomment>
      <translation>记录中的数据流，每种采样率一个。</translation>
    </message>
    <message>
      <source>Run </source>
      <translation>运行 </translation>
    </message>
    <message>
      <source>Which run of the stream to draw. The arrow keys and Page Up / Page Down step through them.</source>
      <translation>要绘制数据流中的哪一段。可用方向键和 Page Up / Page Down 逐个切换。</translation>
    </message>
    <message>
      <source>Stream:</source>
      <translation>数据流：</translation>
    </message>
    <message>
      <source>Open a recording to see its channels.</source>
      <translation>打开记录以查看其通道。</translation>
    </message>
    <message>
      <source>Process a recording, or add EDI / XML sites in the panel on the right.</source>
      <translation>处理一条记录，或在右侧面板中添加 EDI / XML 测点。</translation>
    </message>
    <message>
      <source>Run the 1D inversion from the panel on the right.</source>
      <translation>请在右侧面板中运行一维反演。</translation>
    </message>
    <message>
      <source>Tick two or more sites in the panel on the right.</source>
      <translation>在右侧面板中勾选两个或更多测点。</translation>
    </message>
    <message>
      <source>Run the 2D inversion from the panel on the right.</source>
      <translation>请在右侧面板中运行二维反演。</translation>
    </message>
    <message>
      <source>Recording</source>
      <translation>记录</translation>
    </message>
    <message>
      <source>Phoenix MTU-5C and legacy MTU, Metronix ATS, Zonge Z3D and LEMI-424 are recognised from the files. Open a recording folder, or one file to read only that stream.</source>
      <translation>可从文件识别 Phoenix MTU-5C 和旧版 MTU、Metronix ATS、Zonge Z3D 及 LEMI-424。打开记录文件夹，或打开单个文件以仅读取该数据流。</translation>
    </message>
    <message>
      <source>found by the reader</source>
      <translation>由读取器识别</translation>
    </message>
    <message>
      <source>Phoenix and Metronix: a calibration file or a folder of them (searched through), used instead of what the reader finds near the recording - its folder, the two above it, and any folder there named for calibrations.</source>
      <translation>Phoenix 和 Metronix：一个标定文件或包含标定文件的文件夹（将逐级搜索），用于替代读取器在记录附近找到的标定文件——记录所在文件夹、其上两级文件夹，以及其中以标定命名的任何文件夹。</translation>
    </message>
    <message>
      <source>Calibration</source>
      <translation>校准</translation>
    </message>
    <message>
      <source>as recorded</source>
      <translation>按记录</translation>
    </message>
    <message>
      <source>The coil on {0}. Phoenix receivers record it only when they detect the coil; otherwise choose its calibration here. The list holds the coil calibrations in the Calibration folder, or found near the recording.</source>
      <translation>{0} 上的线圈。Phoenix 接收机仅在检测到线圈时才记录它；否则请在此选择其标定文件。列表包含 Calibration 文件夹中或记录文件附近找到的线圈标定文件。</translation>
    </message>
    <message>
      <source>{0} coil ({1})</source>
      <translation>{0}线圈（{1}）</translation>
    </message>
    <message>
      <source>Which way {0} points, in degrees clockwise from north: 0 north, 90 east, 180 south, 270 west. Leave it as recorded unless the layout differs from what the receiver was told - {1} laid out to the {2} is {3}. Processing turns every channel into the frame of Hx. A remote reference keeps its own directions, which do not change the impedance.</source>
      <translation>{0} 的指向，以自北顺时针的度数表示：0 为北，90 为东，180 为南，270 为西。除非实际布设与接收机中设置的不同，否则保持记录值——{1} 朝 {2} 布设即为 {3}。处理时会将所有通道旋转到 Hx 的坐标系。远参考保持其自身方向，不会改变阻抗。</translation>
    </message>
    <message>
      <source>Directions</source>
      <translation>方向</translation>
    </message>
    <message>
      <source>LEMI-424 files hold the electric field in mV, not mV/km; the dipole lengths convert it. Other formats store them.</source>
      <translation>LEMI-424 文件中的电场单位为 mV，而非 mV/km；需用偶极长度进行换算。其他格式会存储偶极长度。</translation>
    </message>
    <message>
      <source>LEMI dipoles</source>
      <translation>LEMI 偶极</translation>
    </message>
    <message>
      <source>No recording loaded.</source>
      <translation>未载入记录。</translation>
    </message>
    <message>
      <source>Remote reference</source>
      <translation>远参考</translation>
    </message>
    <message>
      <source>A recording made at the same time at a quiet site. Its magnetic fields are the instruments of the regression, which keeps noise local to this site from biasing the impedance downward. Optional.</source>
      <translation>在安静场地同步采集的记录。其磁场作为回归的工具变量，可防止本测点的局部噪声使阻抗估计偏低。可选。</translation>
    </message>
    <message>
      <source>Open remote…</source>
      <translation>打开远参考…</translation>
    </message>
    <message>
      <source>No remote reference.</source>
      <translation>无远参考。</translation>
    </message>
    <message>
      <source>Processing</source>
      <translation>处理</translation>
    </message>
    <message>
      <source>Windows are tapered, decimated level by level and Fourier transformed; in each band a robust regression (Huber, then a redescending cut) solves E = Z·H.</source>
      <translation>各窗口经过锥化、逐级抽取和傅里叶变换；在每个频带中，以稳健回归（先 Huber，再再下降截断）求解 E = Z·H。</translation>
    </message>
    <message>
      <source>Which of the recording's sample rates to process. All of them are processed separately and merged band by band.</source>
      <translation>要处理记录中的哪个采样率。选择全部时将分别处理，并逐频带合并。</translation>
    </message>
    <message>
      <source>Sample rates</source>
      <translation>采样率</translation>
    </message>
    <message>
      <source>Window</source>
      <translation>窗口</translation>
    </message>
    <message>
      <source>Decimation levels; auto adds levels while a band still holds enough windows.</source>
      <translation>抽取级数；自动模式会在频带仍有足够窗口时继续增加级数。</translation>
    </message>
    <message>
      <source>Decimate by</source>
      <translation>抽取倍数</translation>
    </message>
    <message>
      <source>Huber cut, in residual standard deviations.</source>
      <translation>Huber 截断阈值，以残差标准差为单位。</translation>
    </message>
    <message>
      <source>Redescending cut: residuals well past it get no weight.</source>
      <translation>再下降截断：远超此值的残差权重为零。</translation>
    </message>
    <message>
      <source>Robust cuts</source>
      <translation>稳健截断</translation>
    </message>
    <message>
      <source>1 (Hamming)</source>
      <translation>1（Hamming 窗）</translation>
    </message>
    <message>
      <source>Tapers per window. 3 or 5 Slepian tapers (multitaper) give a band several independent estimates from each window: smaller errors at the longest periods of each level, where windows are few, for a little frequency smoothing.</source>
      <translation>每个时窗的锥形窗数。3 或 5 个 Slepian 锥形窗（多窗）可从每个时窗为一个频带给出多个独立估计：在窗口较少的各级最长周期处误差更小，代价是轻微的频率平滑。</translation>
    </message>
    <message>
      <source>Tapers</source>
      <translation>锥形窗</translation>
    </message>
    <message>
      <source>Limit the pull of noisy Hx, Hy (bounded influence)</source>
      <translation>限制噪声 Hx、Hy 的影响（有界影响）</translation>
    </message>
    <message>
      <source>Also downweight windows whose magnetic fields are unusually large - a burst of noise in Hx or Hy - which the usual robust weights let through.</source>
      <translation>同时对磁场异常大的窗口降权——即 Hx 或 Hy 中的突发噪声，常规稳健权重无法排除这些噪声。</translation>
    </message>
    <message>
      <source>Coherence presorting: in each band, leave out stretches of 10 windows where E and H are less coherent than this. Helps a single site; with a remote reference it can drop good data.</source>
      <translation>相干度预筛选：在每个频带中，剔除 E 与 H 相干度低于此值的连续 10 个窗口段。适用于单站处理；使用远参考时可能剔除有效数据。</translation>
    </message>
    <message>
      <source>Min coherence</source>
      <translation>最小相干度</translation>
    </message>
    <message>
      <source>Error bars from the data's spread (jackknife)</source>
      <translation>由数据离散度估计误差棒（刀切法 jackknife）</translation>
    </message>
    <message>
      <source>Estimate each band again without each twentieth of the record; the spread of those estimates is the error. Makes no assumption about the noise.</source>
      <translation>每次剔除记录的二十分之一后重新估算各频带；这些估算值的离散度即为误差。不对噪声作任何假设。</translation>
    </message>
    <message>
      <source>Stack windows of several lengths (multi-window)</source>
      <translation>叠加多种长度的窗口（多窗口）</translation>
    </message>
    <message>
      <source>Each band also uses the windows four times longer or shorter at its frequencies (multi-window stacking, Ernst et al. 2001). Error bars then come from the jackknife, since those windows share the same stretch of record.</source>
      <translation>每个频带还会使用其频率下长四倍或短四倍的窗口（多窗口叠加，Ernst et al. 2001）。由于这些窗口共享同一段记录，误差棒改由刀切法估计。</translation>
    </message>
    <message>
      <source>For noise that grows with the signal, from more than one source: sort the points into up to this many noise classes, weight each by its own noise level, and stop once the residuals are close to Gaussian (stable index 1.8).</source>
      <translation>适用于随信号增大且来源不止一个的噪声：将数据点分为至多此数量的噪声类别，各类按自身噪声水平加权，当残差接近高斯分布（稳定指数 1.8）时停止。</translation>
    </message>
    <message>
      <source>Noise classes</source>
      <translation>噪声类别</translation>
    </message>
    <message>
      <source>Bands with fewer independent estimates than this are dropped.</source>
      <translation>独立估计数少于此值的频带将被剔除。</translation>
    </message>
    <message>
      <source>Min estimates</source>
      <translation>最少估计数</translation>
    </message>
    <message>
      <source>Prewhiten (first difference)</source>
      <translation>预白化（一阶差分）</translation>
    </message>
    <message>
      <source>Tipper from Hz</source>
      <translation>由 Hz 计算倾子</translation>
    </message>
    <message>
      <source>Allow uncalibrated channels</source>
      <translation>允许未标定通道</translation>
    </message>
    <message>
      <source>Process channels still in recorded units. The impedance is then wrong in scale and phase; for checks only.</source>
      <translation>以原始记录单位处理通道。此时阻抗的幅值和相位都是错误的；仅用于检查。</translation>
    </message>
    <message>
      <source>EMTF bands</source>
      <translation>EMTF 频带</translation>
    </message>
    <message>
      <source>Frequencies per decade, each band spanning about a factor of 2 so that neighbours share data: continuous curves, as commercial processing gives. EMTF bands do not overlap: independent points, better for inversion.</source>
      <translation>每十倍频程的频点数，每个频带约跨 2 倍，使相邻频带共享数据：得到连续曲线，与商业处理结果一致。EMTF 频带互不重叠：得到相互独立的数据点，更适合反演。</translation>
    </message>
    <message>
      <source>Frequencies / decade</source>
      <translation>频点数 / 十倍频程</translation>
    </message>
    <message>
      <source>EMTF default bands</source>
      <translation>EMTF 默认频带</translation>
    </message>
    <message>
      <source>An EMTF band-setup file (bs_*.cfg) to use its bands.</source>
      <translation>EMTF 频带设置文件（bs_*.cfg），使用其中的频带。</translation>
    </message>
    <message>
      <source>Band setup</source>
      <translation>频带设置</translation>
    </message>
    <message>
      <source>Interference that repeats exactly on the receiver's clock, in seconds (e.g. 4, 30): its waveform is averaged over the cycles around each one and subtracted before processing. That removes only the narrow lines at its harmonics. Filled in when the recording is read and such interference is found; clear it to keep the data as recorded.</source>
      <translation>按接收机时钟精确重复的干扰周期，单位为秒（如 4、30）：在每个周期前后的若干周期上对其波形取平均，并在处理前减去。这样只会去除其谐波处的窄谱线。读取记录时若发现此类干扰会自动填写；清空则保持数据原样。</translation>
    </message>
    <message>
      <source>Periodic noise (s)</source>
      <translation>周期性噪声 (s)</translation>
    </message>
    <message>
      <source>How many repeats of the periodic noise are averaged into the waveform taken off each one. Fewer follow interference whose shape drifts (each line removed is then a little wider); more keep more of the field.</source>
      <translation>从每个周期中扣除的波形所平均的周期噪声重复次数。次数越少，越能跟踪形态漂移的干扰（但每条被去除的谱线会略宽）；次数越多，保留的场信号越多。</translation>
    </message>
    <message>
      <source>Repeats averaged</source>
      <translation>重复测量已平均</translation>
    </message>
    <message>
      <source>Notch the grid's hum and its harmonics out of every run before processing. When the sample rate puts the hum inside the record (60 Hz in 150 Hz data) it leaks into bands far from it and passes for a phase near 0, which a remote site on the same grid does not remove. Set when the recording is read and hum is found.</source>
      <translation>处理前，从每个记录段中陷波滤除电网工频干扰及其谐波。当采样率使工频落在记录频带内（如 150 Hz 数据中的 60 Hz）时，它会泄漏到远离它的频带，并表现为接近 0 的相位，而位于同一电网上的远参考站无法将其消除。读取记录时若检测到工频干扰，将自动设置此项。</translation>
    </message>
    <message>
      <source>Power line</source>
      <translation>电力线</translation>
    </message>
    <message>
      <source>Process time series</source>
      <translation>处理时间序列</translation>
    </message>
    <message>
      <source>The processed site is added to the sites and opens on the Sounding tab.</source>
      <translation>处理后的测点将加入测点列表，并在“测深”标签页中打开。</translation>
    </message>
    <message>
      <source>Sites processed elsewhere</source>
      <translation>外部处理的测点</translation>
    </message>
    <message>
      <source>EDI, EMTF XML, Z- and J-files skip this step.</source>
      <translation>EDI、EMTF XML、Z 文件和 J 文件跳过此步骤。</translation>
    </message>
    <message>
      <source>Add EDI / XML sites…</source>
      <translation>添加 EDI / XML 测点…</translation>
    </message>
    <message>
      <source>Sites</source>
      <translation>测点</translation>
    </message>
    <message>
      <source>Add EDI / XML…</source>
      <translation>添加 EDI / XML…</translation>
    </message>
    <message>
      <source>Example site</source>
      <translation>示例场地</translation>
    </message>
    <message>
      <source>NMX20, a USMTArray long-period site in New Mexico (EMTF XML).</source>
      <translation>NMX20，位于新墨西哥州的 USMTArray 长周期测点 (EMTF XML)。</translation>
    </message>
    <message>
      <source>The selected site is drawn on the Sounding and Dimensionality tabs, and is the one the 1D model tab inverts.</source>
      <translation>所选测点绘制在“测深”和“维性”标签页中，也是“一维模型”标签页所反演的测点。</translation>
    </message>
    <message>
      <source>Selected site</source>
      <translation>所选测点</translation>
    </message>
    <message>
      <source>Export EDI / XML…</source>
      <translation>导出 EDI / XML…</translation>
    </message>
    <message>
      <source>Write the selected site as EDI and EMTF XML to a folder.</source>
      <translation>将所选测点以 EDI 和 EMTF XML 格式写入文件夹。</translation>
    </message>
    <message>
      <source>Sounding display</source>
      <translation>测深显示</translation>
    </message>
    <message>
      <source>Zxy</source>
      <translation>Zxy</translation>
    </message>
    <message>
      <source>Zyx</source>
      <translation>Zyx</translation>
    </message>
    <message>
      <source>det(Z)</source>
      <translation>det(Z)</translation>
    </message>
    <message>
      <source>Components</source>
      <translation>分量</translation>
    </message>
    <message>
      <source>Error bars</source>
      <translation>误差棒</translation>
    </message>
    <message>
      <source>1D model's fit</source>
      <translation>1D 模型拟合</translation>
    </message>
    <message>
      <source>Draw the 1D inversion's predicted curve when the selected site has been inverted.</source>
      <translation>所选测点已反演时，绘制一维反演的预测曲线。</translation>
    </message>
    <message>
      <source>1D model →</source>
      <translation>1D 模型 →</translation>
    </message>
    <message>
      <source>Invert the selected site for a layered model.</source>
      <translation>将所选测点反演为层状模型。</translation>
    </message>
    <message>
      <source>Profile →</source>
      <translation>剖面 →</translation>
    </message>
    <message>
      <source>Tick the sites of a line, check their phase tensors and invert them in 2D.</source>
      <translation>勾选一条测线上的测点，检查其相位张量并进行二维反演。</translation>
    </message>
    <message>
      <source>Site</source>
      <translation>测点</translation>
    </message>
    <message>
      <source>Invert</source>
      <translation>反演</translation>
    </message>
    <message>
      <source>Occam's smoothest layered model that fits the site to the target RMS.</source>
      <translation>以目标 RMS 拟合该测点的 Occam 最光滑层状模型。</translation>
    </message>
    <message>
      <source>Data and layers</source>
      <translation>数据与图层</translation>
    </message>
    <message>
      <source>Floor on the relative impedance error: 0.05 = 5 % of |Z|, about 10 % in apparent resistivity and 1.4° in phase.</source>
      <translation>相对阻抗误差下限：0.05 = |Z| 的 5 %，约相当于视电阻率 10 %、相位 1.4°。</translation>
    </message>
    <message>
      <source>Error floor</source>
      <translation>误差下限</translation>
    </message>
    <message>
      <source>Static shift</source>
      <translation>静态偏移</translation>
    </message>
    <message>
      <source>Solve for a shift per mode</source>
      <translation>为每个模式求解偏移</translation>
    </message>
    <message>
      <source>One multiplier of each mode's apparent resistivity. From MT alone it is only relative between the modes; a TEM sounding fixes its absolute level.</source>
      <translation>每个模式视电阻率的单一乘数。仅凭 MT 只能确定各模式之间的相对值；TEM 测深可确定其绝对水平。</translation>
    </message>
    <message>
      <source>A central-loop TDEM sounding at the site: gate time (s) and response columns, or a .npz with times and response.</source>
      <translation>该测点的中心回线 TDEM 测深：包含时窗时间（s）与响应列的文件，或包含时间与响应的 .npz 文件。</translation>
    </message>
    <message>
      <source>TEM sounding</source>
      <translation>TEM 测深</translation>
    </message>
    <message>
      <source>TEM loop</source>
      <translation>TEM 回线</translation>
    </message>
    <message>
      <source>TEM measures no electric field, so it carries no static shift: fitted jointly, it fixes the shift's absolute level.</source>
      <translation>TEM 不测量电场，因此不存在静态偏移；联合拟合时可确定静态偏移的绝对水平。</translation>
    </message>
    <message>
      <source>Water content</source>
      <translation>含水量</translation>
    </message>
    <message>
      <source>Convert the model (Waxman-Smits)</source>
      <translation>转换模型 (Waxman-Smits)</translation>
    </message>
    <message>
      <source>Pore water</source>
      <translation>孔隙水</translation>
    </message>
    <message>
      <source>Rock</source>
      <translation>岩石</translation>
    </message>
    <message>
      <source>Run 1D inversion</source>
      <translation>运行一维反演</translation>
    </message>
    <message>
      <source>No 1D model yet.</source>
      <translation>暂无一维模型。</translation>
    </message>
    <message>
      <source>The layered model and its fit as CSV, with the site's EDI.</source>
      <translation>层状模型及其拟合结果（CSV），附该测点的 EDI。</translation>
    </message>
    <message>
      <source>Profile sites</source>
      <translation>剖面测点</translation>
    </message>
    <message>
      <source>The ticked sites, in this order, form the profile. Their distances come from their coordinates, or from the spacing below.</source>
      <translation>勾选的测点按此顺序构成剖面。其距离取自坐标，或取自下方的间距。</translation>
    </message>
    <message>
      <source>Used only when the sites carry no latitude and longitude.</source>
      <translation>仅在测点不含经纬度时使用。</translation>
    </message>
    <message>
      <source>Site spacing (m)</source>
      <translation>测点间距 (m)</translation>
    </message>
    <message>
      <source>Ellipse colour</source>
      <translation>椭圆颜色</translation>
    </message>
    <message>
      <source>Strike and modes</source>
      <translation>走向与模式</translation>
    </message>
    <message>
      <source>Modes</source>
      <translation>模式</translation>
    </message>
    <message>
      <source>normal to the profile</source>
      <translation>垂直于剖面</translation>
    </message>
    <message>
      <source>Geoelectric strike, degrees clockwise from north. Check it against the phase tensors before inverting.</source>
      <translation>电性走向，以自正北顺时针的度数表示。反演前请对照相位张量进行检查。</translation>
    </message>
    <message>
      <source>Strike (°)</source>
      <translation>走向 (°)</translation>
    </message>
    <message>
      <source>The impedances are rotated to the strike: TE is the electric field along it, TM across it. Read the strike off the Phase tensors tab, where Φmax and Φmin part.</source>
      <translation>阻抗已旋转至走向方向：TE 为沿走向的电场，TM 为垂直走向的电场。可在“相位张量”标签页中 Φmax 与 Φmin 分离处读取走向。</translation>
    </message>
    <message>
      <source>Frequencies inverted, spread evenly in log over the first site's. Each costs one 2D forward solve per mode.</source>
      <translation>参与反演的频率，在第一个测点的频率范围内按对数均匀分布。每个频率在每种模式下需进行一次二维正演求解。</translation>
    </message>
    <message>
      <source>SimPEG solves the 2D problem on a mesh laid out from the sites and the frequencies, with air above and padding around.</source>
      <translation>SimPEG 在由测点和频率布设的网格上求解二维问题，上方为空气层，四周设有扩展区。</translation>
    </message>
    <message>
      <source>Run 2D inversion</source>
      <translation>运行二维反演</translation>
    </message>
    <message>
      <source>No 2D section yet.</source>
      <translation>暂无二维断面。</translation>
    </message>
    <message>
      <source>Export section…</source>
      <translation>导出断面…</translation>
    </message>
    <message>
      <source>The section as NPZ and CSV.</source>
      <translation>断面（NPZ 和 CSV）。</translation>
    </message>
    <message>
      <source>Open MT recording folder</source>
      <translation>打开 MT 记录文件夹</translation>
    </message>
    <message>
      <source>Open MT time-series file</source>
      <translation>打开 MT 时间序列文件</translation>
    </message>
    <message>
      <source>Open remote-reference recording folder</source>
      <translation>打开远参考记录文件夹</translation>
    </message>
    <message>
      <source>Calibration folder</source>
      <translation>校准文件夹</translation>
    </message>
    <message>
      <source>EMTF band setup</source>
      <translation>EMTF 频带设置</translation>
    </message>
    <message>
      <source>Add MT sites</source>
      <translation>添加 MT 测点</translation>
    </message>
    <message>
      <source>Reading {0} …</source>
      <translation>正在读取 {0} …</translation>
    </message>
    <message>
      <source>All sample rates</source>
      <translation>所有采样率</translation>
    </message>
    <message>
      <source>{0:g} Hz ({1} run{2})</source>
      <translation>{0:g} Hz（{1} 段）</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0}&lt;/b&gt; · {1} run(s), {2}</source>
      <translation>&lt;b&gt;{0}&lt;/b&gt; · {1} 次运行，{2}</translation>
    </message>
    <message>
      <source> of {0}</source>
      <translation> / {0}</translation>
    </message>
    <message>
      <source>{0} UTC, {1}</source>
      <translation>{0} UTC，{1}</translation>
    </message>
    <message>
      <source>No site selected.</source>
      <translation>未选择测点。</translation>
    </message>
    <message>
      <source>{0} site ticked; the profile needs two or more.</source>
      <translation>已勾选 {0} 个测点；剖面需要两个或更多测点。</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0} sites over {1:.0f} m&lt;/b&gt;; {2}.</source>
      <translation>&lt;b&gt;{0} 个测点，跨度 {1:.0f} m&lt;/b&gt;；{2}。</translation>
    </message>
    <message>
      <source>Tick a component to draw in the panel on the right.</source>
      <translation>勾选要在右侧面板中绘制的分量。</translation>
    </message>
    <message>
      <source>Cannot draw this sounding: {0}</source>
      <translation>无法绘制此测深：{0}</translation>
    </message>
    <message>
      <source>No phase tensor: {0}</source>
      <translation>无相位张量：{0}</translation>
    </message>
    <message>
      <source>Tick two or more sites in the panel on the right to see their phase tensors along the profile.</source>
      <translation>在右侧面板中勾选两个或更多测点，以查看其沿剖面的相位张量。</translation>
    </message>
    <message>
      <source>Cannot draw the phase tensors: {0}</source>
      <translation>无法绘制相位张量：{0}</translation>
    </message>
    <message>
      <source>Export MT results to folder</source>
      <translation>导出 MT 结果到文件夹</translation>
    </message>
    <message>
      <source>Magnetotelluric input formats</source>
      <translation>大地电磁输入格式</translation>
    </message>
    <message>
      <source>Choose data folder · AI classification…</source>
      <extracomment>How many times a module is offered the run's data before giving up on it. Subfolders of the run directory each studio module's work lands in, so the activity strip can offer a button straight to this step's own outputs rather than only to the run folder. How long a resize must pause before the figures are scaled again (ms). Each step as the run reports it - ``phase`` 'start' with the controller's reason, 'done' with its summary and status - so the chat can narrate the run as it goes.</extracomment>
      <translation>选择数据文件夹 · AI 分类…</translation>
    </message>
    <message>
      <source>No data folder selected</source>
      <translation>未选择数据文件夹</translation>
    </message>
    <message>
      <source>File</source>
      <translation>文件</translation>
    </message>
    <message>
      <source>Role (editable)</source>
      <translation>角色（可编辑）</translation>
    </message>
    <message>
      <source>Confidence</source>
      <translation>置信度</translation>
    </message>
    <message>
      <source>Evidence</source>
      <translation>依据</translation>
    </message>
    <message>
      <source>&lt;b&gt;Or add files yourself&lt;/b&gt;&lt;br&gt;For data spread across several folders, or when no AI model is configured (folder classification needs one). Pick what the file is, then Add data.</source>
      <translation>&lt;b&gt;或手动添加文件&lt;/b&gt;&lt;br&gt;适用于数据分散在多个文件夹中，或未配置 AI 模型（文件夹分类需要 AI 模型）的情况。先选择文件类型，再点击“添加数据”。</translation>
    </message>
    <message>
      <source>Add data…</source>
      <translation>添加数据…</translation>
    </message>
    <message>
      <source>Remove selected</source>
      <translation>移除所选</translation>
    </message>
    <message>
      <source>Time-lapse surveys run in the displayed order; select a survey and move it up or down to reorder. Your request and workflow context are sent to the selected AI provider.</source>
      <translation>时移测量按显示顺序运行；选中一次测量并上移或下移即可调整顺序。您的请求和工作流上下文将发送给所选的 AI 服务商。</translation>
    </message>
    <message>
      <source>1 · Data</source>
      <translation>1 · 数据</translation>
    </message>
    <message>
      <source>2 · Live</source>
      <translation>2 · 实时</translation>
    </message>
    <message>
      <source>3 · Results &amp;&amp; report</source>
      <translation>3 · 结果 &amp;&amp; 报告</translation>
    </message>
    <message>
      <source>Output files</source>
      <translation>输出文件</translation>
    </message>
    <message>
      <source>Raw log</source>
      <translation>原始日志</translation>
    </message>
    <message>
      <source>Ready · Select data and describe your goal.</source>
      <translation>就绪 · 请选择数据并描述您的目标。</translation>
    </message>
    <message>
      <source>Actual workflow events will appear here.</source>
      <translation>实际工作流事件将显示在此处。</translation>
    </message>
    <message>
      <source>Also bring each module to the front as it runs</source>
      <translation>运行时同时将各模块切换到前台</translation>
    </message>
    <message>
      <source>The run is followed in the Live tab on this page. Tick this to have the studio also switch to the module doing each step.</source>
      <translation>运行进度在本页的“实时”标签页中跟踪。勾选此项可让 Studio 同时切换到执行各步骤的模块。</translation>
    </message>
    <message>
      <source>Approve each step before it runs</source>
      <translation>每一步运行前需批准</translation>
    </message>
    <message>
      <source>Pause before every step so you can approve it, skip it, or stop the run. The steps and their order are the same either way.</source>
      <translation>在每个步骤前暂停，以便批准、跳过该步骤或停止运行。无论是否暂停，步骤及其顺序都相同。</translation>
    </message>
    <message>
      <source>Run without AI</source>
      <translation>不使用 AI 运行</translation>
    </message>
    <message>
      <source>Run numerical processing and inspect the evidence without contacting an AI provider.</source>
      <translation>在不连接 AI 服务商的情况下运行数值处理并检查结果依据。</translation>
    </message>
    <message>
      <source>Replay a run…</source>
      <translation>回放运行…</translation>
    </message>
    <message>
      <source>Watch a finished run again, from the live_replay.json in its output folder. Nothing is recomputed.</source>
      <translation>根据输出文件夹中的 live_replay.json 重新观看已完成的运行，不会重新计算。</translation>
    </message>
    <message>
      <source>Save this run to Project</source>
      <translation>将此运行保存到工程</translation>
    </message>
    <message>
      <source>View models &amp;&amp; compare runs</source>
      <translation>查看模型 &amp;&amp; 比较运行</translation>
    </message>
    <message>
      <source>View data fit</source>
      <translation>查看数据拟合</translation>
    </message>
    <message>
      <source>Read interpretation</source>
      <translation>阅读解释</translation>
    </message>
    <message>
      <source>Interpret these models…</source>
      <translation>解释这些模型…</translation>
    </message>
    <message>
      <source>Reuse the completed numerical models. Review the next task before starting.</source>
      <translation>复用已完成的数值模型。开始前请检查下一项任务。</translation>
    </message>
    <message>
      <source>&lt;h2&gt;Workflow&lt;/h2&gt;Data, progress, results and report · {0} ({1}) works from the assistant panel on the right</source>
      <extracomment>How the last run ended, for the assistant to read (agent_describe).</extracomment>
      <translation>&lt;h2&gt;工作流&lt;/h2&gt;数据、进度、结果与报告 · {0}（{1}）在右侧助手面板中工作</translation>
    </message>
    <message>
      <source>{0} does not sort folders; add files below.</source>
      <translation>{0} 不整理文件夹；请在下方添加文件。</translation>
    </message>
    <message>
      <source>{0} scans filenames and short text previews in this folder using your selected AI model. Review file roles below before sending “continue”. No files are moved.</source>
      <translation>{0} 使用所选 AI 模型扫描此文件夹中的文件名和简短文本预览。发送“continue”前请检查下方的文件角色。不会移动任何文件。</translation>
    </message>
    <message>
      <source>{0} does not sort a folder for you: add each file below with its role.</source>
      <translation>{0} 不会自动整理文件夹：请在下方逐个添加文件并指定其角色。</translation>
    </message>
    <message>
      <source>&lt;h1&gt;GeoSAGE&lt;/h1&gt;</source>
      <translation>&lt;h1&gt;GeoSAGE&lt;/h1&gt;</translation>
    </message>
    <message>
      <source>Activity</source>
      <translation>活动</translation>
    </message>
    <message>
      <source>Add input…</source>
      <translation>添加输入…</translation>
    </message>
    <message>
      <source>Choose configuration…</source>
      <translation>选择配置…</translation>
    </message>
    <message>
      <source>Choose results folder…</source>
      <translation>选择结果文件夹…</translation>
    </message>
    <message>
      <source>Explore model</source>
      <translation>浏览模型</translation>
    </message>
    <message>
      <source>Data fit</source>
      <translation>数据拟合</translation>
    </message>
    <message>
      <source>Use the provider configured in Assistant settings to interpret these results.</source>
      <translation>使用助手设置中配置的服务商解读这些结果。</translation>
    </message>
    <message>
      <source>Process locally without contacting an AI provider.</source>
      <translation>在本地处理，不连接 AI 服务提供商。</translation>
    </message>
    <message>
      <source>Choose your inputs to begin.</source>
      <translation>选择输入以开始。</translation>
    </message>
    <message>
      <source>&lt;h2&gt;{0}&lt;/h2&gt;Choose a task, check the inputs, then explore the results.</source>
      <translation>&lt;h2&gt;{0}&lt;/h2&gt;选择任务，检查输入，然后浏览结果。</translation>
    </message>
    <message>
      <source>Could not prepare the next task: {0}</source>
      <translation>无法准备下一任务：{0}</translation>
    </message>
    <message>
      <source>Existing models selected · Check the inputs and AI settings, then start when ready.</source>
      <translation>已选择现有模型 · 请检查输入和 AI 设置，准备就绪后开始。</translation>
    </message>
    <message>
      <source>The previous run remains available in Results and Project history.</source>
      <translation>先前的运行仍可在“结果”和“工程历史”中找到。</translation>
    </message>
    <message>
      <source>This run is not in the current Project. Reopen its Project to view or save it.</source>
      <translation>此运行不在当前工程中。请重新打开其所属工程以查看或保存。</translation>
    </message>
    <message>
      <source>Files are local · Not saved to Project history yet</source>
      <translation>文件位于本地 · 尚未保存到工程历史</translation>
    </message>
    <message>
      <source>Saved locally in Project history</source>
      <translation>已在本地保存到工程历史</translation>
    </message>
    <message>
      <source>Could not save: {0}. Your output files remain available.</source>
      <translation>无法保存：{0}。输出文件仍可使用。</translation>
    </message>
    <message>
      <source>Select the folder containing survey data and supporting files</source>
      <translation>选择包含测量数据和辅助文件的文件夹</translation>
    </message>
    <message>
      <source>Folder selected · Send your goal to {0} to scan and classify files.</source>
      <translation>已选择文件夹 · 将目标发送给 {0} 以扫描并分类文件。</translation>
    </message>
    <message>
      <source>Running · {0:.0f}s elapsed · Latest backend event shown above</source>
      <translation>运行中 · 已用时 {0:.0f}s · 上方显示最新后端事件</translation>
    </message>
    <message>
      <source>Select model output folder</source>
      <translation>选择模型输出文件夹</translation>
    </message>
    <message>
      <source>Select data files</source>
      <translation>选择数据文件</translation>
    </message>
    <message>
      <source>Waiting for data · Add files here, then send “continue” to {0}.</source>
      <translation>等待数据 · 在此添加文件，然后向 {0} 发送“continue”。</translation>
    </message>
    <message>
      <source>Describe your goal and add the data to analyze first.</source>
      <translation>请先描述目标并添加要分析的数据。</translation>
    </message>
    <message>
      <source>Data no longer exists: {0}</source>
      <translation>数据已不存在：{0}</translation>
    </message>
    <message>
      <source>Configure an API provider or sign in with a CLI provider in Assistant settings.</source>
      <translation>请在助手设置中配置 API 提供方，或使用 CLI 提供方登录。</translation>
    </message>
    <message>
      <source>Action needed · {0}</source>
      <translation>需要操作 · {0}</translation>
    </message>
    <message>
      <source>Starting · You can continue using other Studio modules.</source>
      <translation>正在启动 · 可继续使用 Studio 的其他模块。</translation>
    </message>
    <message>
      <source>Note sent · {0} reads it {1}.</source>
      <translation>备注已发送 · {0} 将在{1}读取。</translation>
    </message>
    <message>
      <source>Pausing · {0} stops before its next step; the step running now finishes first.</source>
      <translation>正在暂停 · {0} 将在下一步之前停止；当前正在运行的步骤会先完成。</translation>
    </message>
    <message>
      <source>Paused · {0} is waiting before its next step.</source>
      <translation>已暂停 · {0} 正在等待执行下一步。</translation>
    </message>
    <message>
      <source>This run has no model to read notes; pause and stop still work.</source>
      <translation>此运行没有可读取备注的模型；暂停和停止仍可用。</translation>
    </message>
    <message>
      <source>Replay a run</source>
      <translation>回放运行</translation>
    </message>
    <message>
      <source>A run is going · Replay it once it has finished.</source>
      <translation>正在运行 · 完成后可回放。</translation>
    </message>
    <message>
      <source>Could not open the recording · {0}</source>
      <translation>无法打开记录 · {0}</translation>
    </message>
    <message>
      <source>Replaying {0}'s run{1} · nothing is recomputed.</source>
      <translation>正在回放 {0} 的运行{1} · 不重新计算任何内容。</translation>
    </message>
    <message>
      <source>Saved the frame · {0}</source>
      <translation>已保存画面 · {0}</translation>
    </message>
    <message>
      <source>Could not save the frame to {0}.</source>
      <translation>无法将帧保存到 {0}。</translation>
    </message>
    <message>
      <source>Complete · Report and output files are ready.</source>
      <translation>已完成 · 报告和输出文件已就绪。</translation>
    </message>
    <message>
      <source>Computation complete · No report was generated; inspect Activity and output files.</source>
      <translation>计算完成 · 未生成报告；请查看活动记录和输出文件。</translation>
    </message>
    <message>
      <source>Did not complete · {0}, {1}.</source>
      <translation>未完成 · {0}，{1}。</translation>
    </message>
    <message>
      <source>Complete · {0} to check before relying on the results, {1}.</source>
      <translation>已完成 · 使用结果前需检查 {0}，{1}。</translation>
    </message>
    <message>
      <source>Source files preserved · Explore the models or save this run to Project history.</source>
      <translation>源文件已保留 · 可浏览模型或将此运行保存到工程历史。</translation>
    </message>
    <message>
      <source>Explore the available outputs or save this run to Project history.</source>
      <translation>浏览可用输出，或将本次运行保存到工程历史。</translation>
    </message>
    <message>
      <source>Open the observation, prediction and residual maps.</source>
      <translation>打开观测、预测和残差图。</translation>
    </message>
    <message>
      <source>No observation/prediction files are available for this run.</source>
      <translation>此次运行没有可用的观测/预测文件。</translation>
    </message>
    <message>
      <source>Read numerical summary</source>
      <translation>阅读数值摘要</translation>
    </message>
    <message>
      <source>Could not complete · {0}</source>
      <translation>未能完成 · {0}</translation>
    </message>
    <message>
      <source>Stopping workflow…</source>
      <translation>正在停止工作流…</translation>
    </message>
    <message>
      <source>Finished · {0:.1f}s elapsed</source>
      <translation>已完成 · 耗时 {0:.1f}s</translation>
    </message>
    <message>
      <source>Stopped · Partial files remain in the output folder. You can edit and retry.</source>
      <translation>已停止 · 部分文件保留在输出文件夹中。可修改后重试。</translation>
    </message>
    <message>
      <source>Kriging variogram</source>
      <translation>克里金变差函数</translation>
    </message>
    <message>
      <source>model {0} · nugget {1:.4g} · sill {2:.4g} · range {3:.4g} m · fit RMSE {4:.3g}
Separations are measured in the map frame. Web Mercator metres are stretched by 1/cos(latitude), so a geographic range reads larger than the ground distance it represents.</source>
      <translation>模型 {0} · 块金 {1:.4g} · 基台 {2:.4g} · 变程 {3:.4g} m · 拟合 RMSE {4:.3g}
间距在地图坐标系中量测。Web 墨卡托的米按 1/cos(纬度) 拉伸，因此地理坐标下的变程读数大于其代表的实地距离。</translation>
    </message>
    <message>
      <source>Add results from any survey method using Add to Map… or import a point product.</source>
      <translation>使用“添加到地图…”添加任意测量方法的结果，或导入点状成果。</translation>
    </message>
    <message>
      <source>SURVEY LAYERS</source>
      <translation>测量图层</translation>
    </message>
    <message>
      <source>Geographic surveys</source>
      <translation>地理坐标测量</translation>
    </message>
    <message>
      <source>Local project coordinates</source>
      <translation>本地工程坐标</translation>
    </message>
    <message>
      <source>Load basemap</source>
      <translation>载入底图</translation>
    </message>
    <message>
      <source>Fetch imagery for the visible extent. Optional; surveys remain available offline.</source>
      <translation>获取可见范围内的影像。可选；离线时测量数据仍可用。</translation>
    </message>
    <message>
      <source>Survey locations</source>
      <translation>测量位置</translation>
    </message>
    <message>
      <source>Fit surveys</source>
      <translation>适配测量范围</translation>
    </message>
    <message>
      <source>Export map PNG…</source>
      <translation>导出地图 PNG…</translation>
    </message>
    <message>
      <source> cells</source>
      <translation> 个单元</translation>
    </message>
    <message>
      <source>Cells across the longer map axis. More cells give a finer map
but take longer to calculate. Click Interpolate after changing settings.</source>
      <translation>沿地图长轴方向的单元数。单元越多，地图越精细，
但计算耗时越长。更改设置后请点击“插值”。</translation>
    </message>
    <message>
      <source> m blanking</source>
      <translation> m 置空</translation>
    </message>
    <message>
      <source>no blanking</source>
      <translation>不置空</translation>
    </message>
    <message>
      <source>Also blank cells farther than this from any station, so a wide line
spacing does not read as coverage. Set it near the line spacing:
well below that it cuts into the survey and leaves ribbons along the
lines. The caption under the map reports what the outline needs.</source>
      <translation>同时置空距任一测点超过此距离的单元，使较宽的测线
间距不会被误读为覆盖区域。建议设为接近测线间距：
远小于该值会切入测区，并沿测线留下条带。
地图下方的说明会给出轮廓所需的值。</translation>
    </message>
    <message>
      <source>Stations</source>
      <translation>测点</translation>
    </message>
    <message>
      <source>Draw this survey's stations and line traces over its interpolated
surface. Off by default: the surface already carries those values,
and the markers cover the image. Other surveys keep their traces.</source>
      <translation>在此测量的插值曲面上绘制其测点和测线轨迹。
默认关闭：曲面已包含这些数值，
且标记会遮挡图像。其他测量保留其轨迹。</translation>
    </message>
    <message>
      <source>Interpolate</source>
      <translation>插值</translation>
    </message>
    <message>
      <source>Create a surface for the selected slice using the settings above.
You can keep using the map while it calculates. Higher resolution takes longer.</source>
      <translation>使用上述设置为所选切片生成曲面。
计算期间可继续使用地图。分辨率越高耗时越长。</translation>
    </message>
    <message>
      <source>Variogram…</source>
      <translation>变差函数…</translation>
    </message>
    <message>
      <source>Export grid…</source>
      <translation>导出网格…</translation>
    </message>
    <message>
      <source>Choose a slice and interpolation method to get started.</source>
      <translation>选择切片和插值方法以开始。</translation>
    </message>
    <message>
      <source>Stop interpolation after the current calculation batch.</source>
      <translation>在当前计算批次完成后停止插值。</translation>
    </message>
    <message>
      <source>Select a survey to inspect its saved result.</source>
      <translation>选择一个测量以查看其已保存结果。</translation>
    </message>
    <message>
      <source>{0} saved surveys · {1} · Map snapshots are saved immediately. Removing a layer keeps source results.</source>
      <translation>{0} 个已保存测量 · {1} · 地图快照会立即保存。移除图层不会删除源结果。</translation>
    </message>
    <message>
      <source>Could not read project map: {0}</source>
      <translation>无法读取工程地图：{0}</translation>
    </message>
    <message>
      <source>{0}
{1} · {2}
CRS: {3}
Added: {4}</source>
      <translation>{0}
{1} · {2}
CRS：{3}
添加时间：{4}</translation>
    </message>
    <message>
      <source>Depth {0:.3g} m</source>
      <translation>深度 {0:.3g} m</translation>
    </message>
    <message>
      <source>Model Z = {0:g} m</source>
      <translation>模型 Z = {0:g} m</translation>
    </message>
    <message>
      <source>Cannot load {0}: {1}</source>
      <translation>无法载入 {0}：{1}</translation>
    </message>
    <message>
      <source>A section model has no plan slice to interpolate.</source>
      <translation>断面模型没有可插值的平面切片。</translation>
    </message>
    <message>
      <source>Interpolating…</source>
      <translation>正在插值…</translation>
    </message>
    <message>
      <source>Preparing interpolation… You can keep using the map.</source>
      <translation>正在准备插值… 可继续使用地图。</translation>
    </message>
    <message>
      <source>Interpolation complete — the surface is ready to view or export.</source>
      <translation>插值完成——曲面可供查看或导出。</translation>
    </message>
    <message>
      <source>Could not interpolate: {0} Adjust the settings and try again.</source>
      <translation>无法插值：{0} 请调整设置后重试。</translation>
    </message>
    <message>
      <source>Surface ready. Change settings and click Interpolate to update.</source>
      <translation>曲面已就绪。修改设置后点击“插值”进行更新。</translation>
    </message>
    <message>
      <source>Ready — click Interpolate to create the map surface.</source>
      <translation>就绪 — 点击“插值”以生成地图曲面。</translation>
    </message>
    <message>
      <source>Export grid</source>
      <translation>导出网格</translation>
    </message>
    <message>
      <source>Select a survey slice and a Surface interpolation method first; the export writes that grid.</source>
      <translation>请先选择测量切片和曲面插值方法；导出将写出该网格。</translation>
    </message>
    <message>
      <source>Export interpolated plan grid</source>
      <translation>导出插值平面网格</translation>
    </message>
    <message>
      <source>Wrote {0} grid of {1} ({2}) in {3} to {4}.</source>
      <translation>已将 {1}（{2}）的 {0} 网格以 {3} 格式写入 {4}。</translation>
    </message>
    <message>
      <source>Cannot redraw {0}: {1}</source>
      <translation>无法重绘 {0}：{1}</translation>
    </message>
    <message>
      <source>Central Y section</source>
      <translation>中央 Y 断面</translation>
    </message>
    <message>
      <source>The well to compare; click a well on the map to choose it.</source>
      <translation>用于对比的钻孔；点击地图上的钻孔进行选择。</translation>
    </message>
    <message>
      <source>Well</source>
      <translation>钻孔</translation>
    </message>
    <message>
      <source>Surveys read farther than this from the well are listed below the plot, not drawn.</source>
      <translation>距钻孔超过此距离的测量数据列在图下方，不予绘制。</translation>
    </message>
    <message>
      <source>Surveys within</source>
      <translation>范围内的测量</translation>
    </message>
    <message>
      <source>Down to</source>
      <translation>向下至</translation>
    </message>
    <message>
      <source>Cannot read the wells of {0}: {1}</source>
      <translation>无法读取 {0} 的钻孔：{1}</translation>
    </message>
    <message>
      <source>Map visibility</source>
      <translation>地图可见性</translation>
    </message>
    <message>
      <source>Rename survey</source>
      <translation>重命名测量</translation>
    </message>
    <message>
      <source>Survey name</source>
      <translation>测量名称</translation>
    </message>
    <message>
      <source>Loading optional basemap… Survey results remain available.</source>
      <translation>正在载入可选底图… 测量结果仍可使用。</translation>
    </message>
    <message>
      <source>Basemap loaded.</source>
      <translation>底图已载入。</translation>
    </message>
    <message>
      <source>Basemap unavailable; showing surveys without imagery.</source>
      <translation>底图不可用；仅显示测量，不显示影像。</translation>
    </message>
    <message>
      <source>Basemap unavailable: {0}</source>
      <translation>底图不可用：{0}</translation>
    </message>
    <message>
      <source>Export current project map</source>
      <translation>导出当前工程地图</translation>
    </message>
    <message>
      <source>Map export</source>
      <translation>地图导出</translation>
    </message>
    <message>
      <source>Point product: x,y,value columns</source>
      <translation>点产品：x,y,value 列</translation>
    </message>
    <message>
      <source>Survey method</source>
      <translation>测量方法</translation>
    </message>
    <message>
      <source>Product units</source>
      <translation>产品单位</translation>
    </message>
    <message>
      <source>Units (e.g. mGal, nT, Ω·m, m/s)</source>
      <translation>单位（如 mGal、nT、Ω·m、m/s）</translation>
    </message>
    <message>
      <source>Point product</source>
      <translation>点产品</translation>
    </message>
    <message>
      <source>Available results</source>
      <translation>可用结果</translation>
    </message>
    <message>
      <source>No model resources in this session. Run a module or import a point product CSV.</source>
      <translation>本会话中没有模型资源。请运行一个模块或导入点产品 CSV。</translation>
    </message>
    <message>
      <source>Add available result</source>
      <translation>添加可用结果</translation>
    </message>
    <message>
      <source>Model units</source>
      <translation>模型单位</translation>
    </message>
    <message>
      <source>Units</source>
      <translation>单位</translation>
    </message>
    <message>
      <source>Available result</source>
      <translation>可用结果</translation>
    </message>
    <message>
      <source>Seismic lines: a dot marks distance 0, the arrow points along the line</source>
      <extracomment>The steps the assistant names. Each opens the view and the panel the step is done in (see _go_to); the page itself does not page through them. The lines table: name, then the two endpoints in map coordinates. Where a line's mesh and velocity paths are kept, on its name cell.</extracomment>
      <translation>地震测线：圆点标记距离 0，箭头指向测线方向</translation>
    </message>
    <message>
      <source>{0}: velocity, and the bedrock top where it passes {1:.0f} m/s</source>
      <translation>{0}：速度，以及速度超过 {1:.0f} m/s 处的基岩顶面</translation>
    </message>
    <message>
      <source>3D model</source>
      <translation>3D 模型</translation>
    </message>
    <message>
      <source>Figures</source>
      <translation>图件</translation>
    </message>
    <message>
      <source>Add three synthetic velocity lines that cross one site.</source>
      <translation>添加三条穿过同一测点的合成速度测线。</translation>
    </message>
    <message>
      <source>Add a line…</source>
      <translation>添加测线…</translation>
    </message>
    <message>
      <source>Build a 3D model from seismic lines</source>
      <translation>由地震测线构建三维模型</translation>
    </message>
    <message>
      <source>Join 2D seismic velocity sections into a 3D velocity model and a bedrock surface, for a hydrologic model or to split an ERT model into layers.</source>
      <translation>将二维地震速度断面拼接为三维速度模型和基岩面，用于水文模型或将 ERT 模型划分为若干层。</translation>
    </message>
    <message>
      <source>Add the seismic lines: each line's velocity section, and where it lies on the map.</source>
      <translation>添加地震测线：每条测线的速度断面及其在地图上的位置。</translation>
    </message>
    <message>
      <source>Choose the velocity that marks the top of bedrock, and check it on each line's section.</source>
      <translation>选择标志基岩顶面的速度，并在各测线断面上核查。</translation>
    </message>
    <message>
      <source>Set the 3D grid, and press Build 3D model.</source>
      <translation>设置三维网格，然后点击“构建三维模型”。</translation>
    </message>
    <message>
      <source>Build 3D model</source>
      <extracomment>Each numbered step's title; a finished step gets a tick after it.</extracomment>
      <translation>构建三维模型</translation>
    </message>
    <message>
      <source>Interpolate the lines' velocity and their bedrock tops across the site, onto the 3D grid.</source>
      <translation>将各测线的速度及其基岩顶面在整个场地范围内插值到三维网格上。</translation>
    </message>
    <message>
      <source>1  Seismic lines</source>
      <translation>1  地震测线</translation>
    </message>
    <message>
      <source>Add a line from a folder with velmesh.bms and Vinvmodel.npy.</source>
      <translation>从包含 velmesh.bms 和 Vinvmodel.npy 的文件夹添加测线。</translation>
    </message>
    <message>
      <source>Add a line from a mesh file and a velocity file chosen one by one.</source>
      <translation>分别选择网格文件和速度文件来添加测线。</translation>
    </message>
    <message>
      <source>What a line needs.</source>
      <translation>测线需要的内容。</translation>
    </message>
    <message>
      <source>Place each line on the map by its two ends, in metres. Start is where its section's distance 0 lies.</source>
      <translation>通过两个端点（单位：米）将每条测线放置在地图上。起点为其断面距离 0 所在位置。</translation>
    </message>
    <message>
      <source>2  Bedrock interface</source>
      <translation>2  基岩界面</translation>
    </message>
    <message>
      <source>The top of bedrock is where the velocity first passes this value going down. The Section tab draws it on each line.</source>
      <translation>基岩顶面为自上而下速度首次超过此值的位置。“断面”标签页会在每条测线上绘制该界面。</translation>
    </message>
    <message>
      <source>Bedrock top at</source>
      <translation>基岩顶面位于</translation>
    </message>
    <message>
      <source>Pick every</source>
      <translation>拾取间隔</translation>
    </message>
    <message>
      <source>Send to ERT → Water Content</source>
      <translation>发送到 ERT → 含水量</translation>
    </message>
    <message>
      <source>Send the bedrock top of the line on the Section tab to ERT → Water Content, to split its model into regolith and bedrock.</source>
      <translation>将“断面”选项卡中测线的基岩顶面发送到 ERT → 含水量，用以将其模型划分为风化层和基岩。</translation>
    </message>
    <message>
      <source>3  3D grid</source>
      <translation>3  3D 网格</translation>
    </message>
    <message>
      <source>Linear (griddata)</source>
      <translation>线性 (griddata)</translation>
    </message>
    <message>
      <source>Kriging</source>
      <translation>克里金</translation>
    </message>
    <message>
      <source>Kriging needs the optional 'gstools' package; linear interpolation is used otherwise.</source>
      <translation>克里金需要可选的 'gstools' 包；否则使用线性插值。</translation>
    </message>
    <message>
      <source>Cells across</source>
      <translation>横向单元数</translation>
    </message>
    <message>
      <source>Between lines</source>
      <translation>测线之间</translation>
    </message>
    <message>
      <source>Vertical scale</source>
      <translation>垂直比例</translation>
    </message>
    <message>
      <source>Velocity samples</source>
      <translation>速度样本</translation>
    </message>
    <message>
      <source>Kriging model</source>
      <translation>克里金模型</translation>
    </message>
    <message>
      <source>Range east</source>
      <translation>东向变程</translation>
    </message>
    <message>
      <source>Range north</source>
      <translation>北向变程</translation>
    </message>
    <message>
      <source>Range down</source>
      <translation>垂向变程</translation>
    </message>
    <message>
      <source>Variance (sill)</source>
      <translation>方差（基台值）</translation>
    </message>
    <message>
      <source>Nugget</source>
      <translation>块金值</translation>
    </message>
    <message>
      <source>Save 3D settings</source>
      <translation>保存三维设置</translation>
    </message>
    <message>
      <source>Write the lines and settings to seismic3d_config.json, without building anything.</source>
      <translation>将测线和设置写入 seismic3d_config.json，不进行任何构建。</translation>
    </message>
    <message>
      <source>Select velocity-model folder</source>
      <translation>选择速度模型文件夹</translation>
    </message>
    <message>
      <source>Select mesh</source>
      <translation>选择网格</translation>
    </message>
    <message>
      <source>Select velocity array</source>
      <translation>选择速度数组</translation>
    </message>
    <message>
      <source>Built from {0} lines on a {1} × {2} grid: velocity {3} m/s, bedrock {4} m deep.</source>
      <translation>由 {0} 条测线在 {1} × {2} 网格上构建：速度 {3} m/s，基岩深 {4} m。</translation>
    </message>
    <message>
      <source>Seismic → Structure input format</source>
      <translation>地震 → 构造输入格式</translation>
    </message>
    <message>
      <source>Building…</source>
      <translation>正在构建…</translation>
    </message>
    <message>
      <source>Building the 3D model…</source>
      <translation>正在构建三维模型…</translation>
    </message>
    <message>
      <source>Finished. The model is on the {0} tab.</source>
      <translation>已完成。模型位于“{0}”选项卡。</translation>
    </message>
    <message>
      <source>The build failed: {0}</source>
      <translation>构建失败：{0}</translation>
    </message>
    <message>
      <source>Stopped before it finished. Press Build 3D model to start again.</source>
      <translation>未完成即已停止。按“构建三维模型”重新开始。</translation>
    </message>
    <message>
      <source>Gather</source>
      <translation>道集</translation>
    </message>
    <message>
      <source>travel time (ms)</source>
      <translation>走时 (ms)</translation>
    </message>
    <message>
      <source>Travel-time</source>
      <translation>走时</translation>
    </message>
    <message>
      <source>Velocity model</source>
      <translation>速度模型</translation>
    </message>
    <message>
      <source>Reflection</source>
      <translation>反射</translation>
    </message>
    <message>
      <source>Load seismic data…</source>
      <translation>载入地震数据…</translation>
    </message>
    <message>
      <source>Formats: {0}</source>
      <translation>格式：{0}</translation>
    </message>
    <message>
      <source>Load geophone positions / topography…</source>
      <translation>载入检波器位置 / 地形…</translation>
    </message>
    <message>
      <source>Load a text file of per-geophone x distance and elevation (columns: station distance_m elevation_m, or x z). Picks then carry real positions + topography into the SRT inversion.</source>
      <translation>载入包含各检波器 x 距离和高程的文本文件（列：station distance_m elevation_m，或 x z）。拾取结果将携带实际位置和地形进入 SRT 反演。</translation>
    </message>
    <message>
      <source>Even spacing (no position file).</source>
      <translation>等间距（无位置文件）。</translation>
    </message>
    <message>
      <source>Geometry</source>
      <translation>几何</translation>
    </message>
    <message>
      <source>Record</source>
      <translation>记录</translation>
    </message>
    <message>
      <source>Geophone spacing</source>
      <translation>检波器间距</translation>
    </message>
    <message>
      <source>Geophone 0 x</source>
      <translation>检波器 0 x</translation>
    </message>
    <message>
      <source>Shot position for this record; may be before geophone 0 (negative).</source>
      <translation>此记录的炮点位置；可位于检波器 0 之前（负值）。</translation>
    </message>
    <message>
      <source>Shot x (this record)</source>
      <translation>炮点 x（此记录）</translation>
    </message>
    <message>
      <source>Display / processing</source>
      <translation>显示 / 处理</translation>
    </message>
    <message>
      <source>Clip</source>
      <translation>裁切</translation>
    </message>
    <message>
      <source>Flip polarity</source>
      <translation>反转极性</translation>
    </message>
    <message>
      <source>Normalize trace</source>
      <translation>道归一化</translation>
    </message>
    <message>
      <source>AGC</source>
      <translation>AGC</translation>
    </message>
    <message>
      <source> ms</source>
      <translation> ms</translation>
    </message>
    <message>
      <source>First-arrival picking</source>
      <translation>初至拾取</translation>
    </message>
    <message>
      <source>Manual pick mode (click a trace)</source>
      <translation>手动拾取模式（点击道）</translation>
    </message>
    <message>
      <source>Tip: Ctrl+drag draws a line and picks every trace it crosses.</source>
      <translation>提示：Ctrl+拖动可画线并拾取其穿过的每一道。</translation>
    </message>
    <message>
      <source>A first arrival is picked where the trace, with AGC when AGC is on, first reaches this fraction of its peak in the search window and five times the noise before it (lower = earlier).</source>
      <translation>初至拾取位置为：道（启用 AGC 时为 AGC 处理后的道）首次达到搜索窗内峰值的该比例，且达到其之前噪声五倍的位置（值越小，拾取越早）。</translation>
    </message>
    <message>
      <source>Threshold (of trace peak)</source>
      <translation>阈值（相对道峰值）</translation>
    </message>
    <message>
      <source>The picker looks for first arrivals up to this time.</source>
      <translation>拾取器在此时间之前搜索初至。</translation>
    </message>
    <message>
      <source>Latest first arrival</source>
      <translation>最晚初至</translation>
    </message>
    <message>
      <source>Leave out stray picks and shots</source>
      <translation>剔除离群拾取和炮</translation>
    </message>
    <message>
      <source>Leave out what still strays once the stray picks are picked again: a pick that breaks its shot's first-arrival curve (a first arrival cannot come earlier farther from the shot), and, with all shots picked, a shot whose times disagree with their reciprocals and a pick that still disagrees with the neighbouring shots at its geophone once picked again.</source>
      <translation>剔除离群拾取重新拾取后仍然离群的部分：破坏所在炮初至曲线的拾取（离炮点越远，初至不可能越早）；以及在所有炮均已拾取时，走时与其互易走时不一致的炮，和重新拾取后在其检波器处仍与相邻炮不一致的拾取。</translation>
    </message>
    <message>
      <source>Auto-pick this shot</source>
      <translation>自动拾取本炮</translation>
    </message>
    <message>
      <source>Pick this record's first arrivals as the seismic workflow does; a pick that strays from the shot's first-arrival curve is picked again along it (AIC picker, Maeda 1985).</source>
      <translation>按地震工作流的方式拾取此记录的初至；偏离该炮初至曲线的拾取将沿该曲线重新拾取（AIC 拾取器，Maeda 1985）。</translation>
    </message>
    <message>
      <source>All shots</source>
      <translation>所有炮</translation>
    </message>
    <message>
      <source>Auto-pick every shot record, then check each shot against its reciprocals and each pick against the neighbouring shots at the same geophone. Manual picks are kept.</source>
      <translation>自动拾取所有炮记录，然后将每炮与其互易炮对比检查，并将每个拾取与同一检波器上相邻炮的拾取对比检查。手动拾取将被保留。</translation>
    </message>
    <message>
      <source>Undo</source>
      <translation>撤销</translation>
    </message>
    <message>
      <source>Export picks CSV…</source>
      <translation>导出拾取 CSV…</translation>
    </message>
    <message>
      <source>Save the picks of every shot, not only the one on screen.</source>
      <translation>保存所有炮的拾取结果，而不仅是屏幕上显示的那一炮。</translation>
    </message>
    <message>
      <source>Export travel-time .dat…</source>
      <translation>导出走时 .dat…</translation>
    </message>
    <message>
      <source>Save every shot's picks as travel times for PyGIMLi, as the inversion uses them.</source>
      <translation>将每一炮的拾取结果按反演所用的方式保存为 PyGIMLi 走时数据。</translation>
    </message>
    <message>
      <source>0 picks</source>
      <translation>0 个拾取</translation>
    </message>
    <message>
      <source>Travel times to invert</source>
      <translation>待反演走时</translation>
    </message>
    <message>
      <source>Pick first breaks across shots and set each shot's x on the Gather tab, or skip picking and upload pre-picked times.</source>
      <translation>在各炮中拾取初至，并在“道集”选项卡中设置每炮的 x，或跳过拾取并上传预先拾取的走时。</translation>
    </message>
    <message>
      <source>Upload travel times…</source>
      <translation>上传走时…</translation>
    </message>
    <message>
      <source>Load a pre-picked travel-time file and invert it directly (no picking). Formats: pyGIMLi/BERT .sgt/.dat (sensors + 's g t'), or a CSV/text with columns source_x, receiver_x, time  (or source_x, source_z, receiver_x, receiver_z, time). Times in seconds (milliseconds auto-detected).</source>
      <translation>载入已拾取的走时文件并直接反演（无需拾取）。格式：pyGIMLi/BERT .sgt/.dat（传感器 + 's g t'），或含 source_x、receiver_x、time 列的 CSV/文本文件  （或 source_x、source_z、receiver_x、receiver_z、time）。时间单位为秒（自动识别毫秒）。</translation>
    </message>
    <message>
      <source>Clear the uploaded travel times (go back to using picks).</source>
      <translation>清除上传的走时（恢复使用拾取结果）。</translation>
    </message>
    <message>
      <source>Run SRT inversion</source>
      <translation>运行 SRT 反演</translation>
    </message>
    <message>
      <source>Export velocity model…</source>
      <translation>导出速度模型…</translation>
    </message>
    <message>
      <source>Write the recovered velocity model as npy, the mesh, and a VTK file.</source>
      <translation>将反演得到的速度模型写出为 npy、网格和 VTK 文件。</translation>
    </message>
    <message>
      <source>Traces</source>
      <translation>道</translation>
    </message>
    <message>
      <source>none, or e.g. 1, 5, 12</source>
      <translation>无，或如 1, 5, 12</translation>
    </message>
    <message>
      <source>Shots to leave out of the stack, by record number: a mistimed trigger, a missed blow, wind or traffic. Look through the shots on the Gather tab first.</source>
      <translation>按记录号指定不参与叠加的炮：触发时间错误、锤击落空、风或交通干扰。请先在“道集”选项卡中逐炮检查。</translation>
    </message>
    <message>
      <source>Leave out shots</source>
      <translation>剔除炮</translation>
    </message>
    <message>
      <source>Leave out clipped traces</source>
      <translation>剔除削波道</translation>
    </message>
    <message>
      <source>A trace whose recorder saturated - usually the geophones next to the hammer - has its peaks cut flat, which distorts every wave on it.</source>
      <translation>记录仪饱和的道（通常是锤击点旁的检波器）峰值被削平，会使其上所有波形失真。</translation>
    </message>
    <message>
      <source>Leave out traces with signal before the first arrival</source>
      <translation>剔除初至前有信号的道</translation>
    </message>
    <message>
      <source>Nothing can reach a geophone two metres from the hammer in the first 1.5 ms, so a trace with signal there has a trigger or wiring fault.</source>
      <translation>在最初 1.5 ms 内，任何波都无法到达距锤击点两米的检波器，因此若某道在此时段内有信号，说明存在触发或接线故障。</translation>
    </message>
    <message>
      <source>Clean-up</source>
      <translation>清理</translation>
    </message>
    <message>
      <source>Line up shot timing on the air wave</source>
      <translation>按空气波对齐炮时间</translation>
    </message>
    <message>
      <source>A hammer trigger fires a little early or late on each blow. The sound of the blow crosses the line at the speed of sound, so where it arrives tells each shot's timing error, which is then taken out.</source>
      <translation>锤击触发在每次锤击时都会略早或略晚。锤击声以声速沿测线传播，因此其到达位置可反映每炮的计时误差，随后将其校正。</translation>
    </message>
    <message>
      <source>Remove the air wave</source>
      <translation>去除空气波</translation>
    </message>
    <message>
      <source>Subtract the sound of the blow and mute what is left of it, so it cannot stack into something that looks like a reflection.</source>
      <translation>减去锤击声波并切除其残余，以免叠加后形成类似反射的假象。</translation>
    </message>
    <message>
      <source>The frequencies kept. The filter only looks back in time, so it cannot smear later energy such as ground roll into earlier times.</source>
      <translation>保留的频率。该滤波器仅向过去时间回溯，因此不会把面波等较晚到达的能量涂抹到较早时间。</translation>
    </message>
    <message>
      <source>Keep frequencies</source>
      <translation>保留频率</translation>
    </message>
    <message>
      <source>Values set here</source>
      <translation>在此设置的值</translation>
    </message>
    <message>
      <source>The refraction model</source>
      <translation>折射模型</translation>
    </message>
    <message>
      <source>The refraction model is the Velocity model tab's result, averaged along the stacked part of the line. Only the part the rays reached is used.</source>
      <translation>折射模型为“速度模型”标签页的结果，沿测线已叠加部分取平均。仅使用射线覆盖到的部分。</translation>
    </message>
    <message>
      <source>Velocity from</source>
      <translation>速度来源</translation>
    </message>
    <message>
      <source>How fast the waves travel in the ground below the line.</source>
      <translation>测线下方地层中的波速。</translation>
    </message>
    <message>
      <source>Faster below a certain time</source>
      <translation>某时间以下速度更快</translation>
    </message>
    <message>
      <source>Use a second, faster velocity below a two-way time - for example below the water table, where the refraction on the Travel-time tab shows a faster layer.</source>
      <translation>在某一双程时间以下使用第二个更快的速度，例如在地下水位以下，“走时”标签页中的折射显示存在更快的层。</translation>
    </message>
    <message>
      <source>From</source>
      <translation>从</translation>
    </message>
    <message>
      <source>Velocity there</source>
      <translation>该处速度</translation>
    </message>
    <message>
      <source>Stack</source>
      <translation>叠加</translation>
    </message>
    <message>
      <source>Shot-to-geophone distances that go into the stack. The nearest are clipped or swamped by the blow; the farthest mostly carry ground roll.</source>
      <translation>参与叠加的炮检距。最近的道会被削波或被锤击淹没；最远的道主要是面波。</translation>
    </message>
    <message>
      <source>Offsets</source>
      <translation>偏移距</translation>
    </message>
    <message>
      <source>Spacing of the stacked section's traces. The geophone spacing is a good choice.</source>
      <translation>叠加断面的道间距。建议使用检波器间距。</translation>
    </message>
    <message>
      <source>More settings</source>
      <translation>更多设置</translation>
    </message>
    <message>
      <source>The velocity correction stretches the far traces' wavelets; past this much stretch they are muted rather than stacked.</source>
      <translation>速度校正会拉伸远道的子波；拉伸超过此值时将被切除而不参与叠加。</translation>
    </message>
    <message>
      <source>Stretch limit</source>
      <translation>拉伸限度</translation>
    </message>
    <message>
      <source>A point of the section with fewer traces than this is left blank.</source>
      <translation>断面中道数少于此值的点将置空。</translation>
    </message>
    <message>
      <source>Traces per point, at least</source>
      <translation>每点最少道数</translation>
    </message>
    <message>
      <source>Everything that travels slower than this - ground roll - is muted before stacking.</source>
      <translation>速度低于此值的波（面波）在叠加前被切除。</translation>
    </message>
    <message>
      <source>Ground roll slower than</source>
      <translation>面波速度低于</translation>
    </message>
    <message>
      <source>Stack the line</source>
      <translation>叠加测线</translation>
    </message>
    <message>
      <source>Stop the stack. It stops between steps - checking the traces, cleaning the shots, stacking - so the step under way finishes first.</source>
      <translation>停止叠加。停止发生在步骤之间（检查道、清理炮记录、叠加），因此正在进行的步骤会先完成。</translation>
    </message>
    <message>
      <source>Save the section as a picture (PNG) or as numbers (NumPy .npz, with the velocity and fold).</source>
      <translation>将断面保存为图片 (PNG) 或数值 (NumPy .npz，含速度和覆盖次数)。</translation>
    </message>
    <message>
      <source>Save the stacked section, in depth, as a survey in the Project Map, where it can be read beside the wells.</source>
      <translation>将深度域叠加断面作为测量保存到工程地图，便于与钻孔对照解读。</translation>
    </message>
    <message>
      <source>Solver. The in-house Gauss-Newton inversion exposes its own stopping rule, so the fit assistance below can drive it; the PyGIMLi manager runs once.</source>
      <translation>求解器。内置 Gauss-Newton 反演提供自己的停止准则，因此下方的拟合辅助可驱动它；PyGIMLi 管理器只运行一次。</translation>
    </message>
    <message>
      <source>Smoothness of the velocity model. Lower fits the travel times harder, higher gives a smoother model. Start on the smooth side: the search relaxes downward, continuing each λ from the previous solution.</source>
      <translation>速度模型的光滑度。值越低对走时拟合越紧，值越高模型越光滑。建议从较光滑一侧开始：搜索向下放松，每个 λ 都从上一个解继续。</translation>
    </message>
    <message>
      <source>The inversion is done when one more iteration lowers χ² by less than this. Larger stops sooner; smaller makes sure the fit has really run out of room.</source>
      <translation>当再迭代一次使 χ² 的降低量小于此值时，反演结束。值越大停止越早；值越小越能确保拟合确已无改进空间。</translation>
    </message>
    <message>
      <source>Inversion-mesh quality: the minimum triangle angle. Higher gives a finer, better-conditioned triangulation at more cost per iteration.</source>
      <translation>反演网格质量：三角形最小角。数值越大，三角剖分越精细、条件越好，但每次迭代的计算代价越高。</translation>
    </message>
    <message>
      <source>How deep to invert. PyGIMLi sizes the domain from the array length, which for refraction reaches well past where any ray turns, so the deep cells are unconstrained and only slow the run. Cap it when the ray-path plot shows the bottom of the section is empty.</source>
      <translation>反演深度。PyGIMLi 根据排列长度确定区域大小，对于折射而言远超任何射线的转折深度，因此深部单元不受约束，只会拖慢运行。当射线路径图显示断面底部为空时，可限制该深度。</translation>
    </message>
    <message>
      <source>Invert to depth</source>
      <translation>反演至深度</translation>
    </message>
    <message>
      <source>Largest cell in the inverted domain. Smaller resolves more detail and adds unknowns; leave at auto unless the model looks blocky against what the ray coverage supports.</source>
      <translation>反演区域内的最大单元。数值越小可分辨更多细节，但会增加未知数；除非模型相对于射线覆盖度所能支持的程度显得块状明显，否则保持自动。</translation>
    </message>
    <message>
      <source>Max cell size</source>
      <translation>最大单元尺寸</translation>
    </message>
    <message>
      <source>Secondary nodes</source>
      <translation>次级节点</translation>
    </message>
    <message>
      <source>The inversion at the λ above always runs first and is always kept. If its χ² misses the target band, the same mesh is re-inverted at other λ values and the closest one becomes the displayed model. Each trial continues from the nearest λ already solved, so the later ones are cheap, but every trial is still a full inversion.</source>
      <translation>始终先以上方的 λ 运行反演并保留其结果。若其 χ² 未落入目标范围，则在同一网格上以其他 λ 值重新反演，并显示最接近目标的模型。每次试算都从已求解的最近 λ 继续，因此后续试算开销较小，但每次试算仍是一次完整反演。</translation>
    </message>
    <message>
      <source>χ² = 1 means the model explains the picks to within their assumed error. Raise it if the picks are noisier than that admits.</source>
      <translation>χ² = 1 表示模型在假定误差范围内解释了拾取值。若拾取噪声大于该误差所允许的程度，请调高此值。</translation>
    </message>
    <message>
      <source>Load seismic data</source>
      <translation>载入地震数据</translation>
    </message>
    <message>
      <source>Loading…</source>
      <translation>正在载入…</translation>
    </message>
    <message>
      <source>Loading {0}…</source>
      <translation>正在载入 {0}…</translation>
    </message>
    <message>
      <source>Shot {0}</source>
      <translation>炮 {0}</translation>
    </message>
    <message>
      <source>Not used while the gather's colour range is locked: the image is drawn between the limits typed beside “Lock range”.</source>
      <translation>道集色阶范围锁定时不使用该项：图像按“锁定范围”旁输入的上下限绘制。</translation>
    </message>
    <message>
      <source>Amplitudes beyond this percentile are clipped, so a few strong traces do not wash out the rest.</source>
      <translation>超过此百分位数的振幅将被截断，避免少数强道淹没其他道。</translation>
    </message>
    <message>
      <source>Load geophone positions / topography</source>
      <translation>载入检波器位置 / 地形</translation>
    </message>
    <message>
      <source>Even spacing {0}: {1} geophones, x {2:g} to {3:g} m{4}.</source>
      <translation>等间距 {0}：{1} 个检波器，x 从 {2:g} 到 {3:g} m{4}。</translation>
    </message>
    <message>
      <source>Export picks</source>
      <translation>导出拾取</translation>
    </message>
    <message>
      <source>Export travel-time</source>
      <translation>导出走时</translation>
    </message>
    <message>
      <source>Upload picked travel times</source>
      <translation>上传已拾取的走时</translation>
    </message>
    <message>
      <source>Export velocity model to folder</source>
      <translation>导出速度模型到文件夹</translation>
    </message>
    <message>
      <source>Load a shot file on the Gather tab first: stacking needs several shots recorded along one line (SEG-Y or Geometrics DAT).</source>
      <translation>请先在“道集”选项卡中载入炮文件：叠加需要沿同一测线记录的多炮数据（SEG-Y 或 Geometrics DAT）。</translation>
    </message>
    <message>
      <source>Stacks the {0} shots loaded on the Gather tab, with the geophones and shot positions set there (geophones every {1:g} m).</source>
      <translation>叠加“道集”选项卡中载入的 {0} 炮，使用该处设置的检波器和炮点位置（检波器间距 {1:g} m）。</translation>
    </message>
    <message>
      <source>Stacking…</source>
      <translation>正在叠加…</translation>
    </message>
    <message>
      <source>Export reflection section</source>
      <translation>导出反射断面</translation>
    </message>
    <message>
      <source>Open .py</source>
      <extracomment>Qt's QWIDGETSIZE_MAX, the "no maximum" of setMaximumWidth.</extracomment>
      <translation>打开 .py</translation>
    </message>
    <message>
      <source>Open .ipynb</source>
      <translation>打开 .ipynb</translation>
    </message>
    <message>
      <source>Step-by-step Python for this run: named parameters, the domain calls, and a figure.</source>
      <translation>本次运行的逐步 Python 代码：命名参数、领域函数调用和一幅图。</translation>
    </message>
    <message>
      <source>The same walkthrough as a Jupyter notebook.</source>
      <translation>以 Jupyter notebook 形式提供的相同演练。</translation>
    </message>
    <message>
      <source>Reveal the recipe and the exact-rerun script alongside the walkthrough.</source>
      <translation>在步骤说明旁显示配方和精确重跑脚本。</translation>
    </message>
    <message>
      <source>Run records</source>
      <translation>运行记录</translation>
    </message>
    <message>
      <source>Open this run's settings file, data QC report or log.</source>
      <translation>打开此次运行的设置文件、数据 QC 报告或日志。</translation>
    </message>
    <message>
      <source>Each survey's QC log  ({0}/)</source>
      <translation>各测量的 QC 日志  ({0}/)</translation>
    </message>
    <message>
      <source>Nothing written yet</source>
      <translation>尚未写入任何内容</translation>
    </message>
    <message>
      <source>Reproduce this run outside the GUI: &lt;b&gt;{0}&lt;/b&gt;</source>
      <translation>在 GUI 之外复现此运行：&lt;b&gt;{0}&lt;/b&gt;</translation>
    </message>
    <message>
      <source>Describe a goal in the assistant panel on the right and choose &lt;b&gt;Auto to report&lt;/b&gt;. Each step the assistant decides on appears here as it happens: why it chose it, where it worked, and what it found.</source>
      <translation>在右侧助手面板中描述目标，并选择&lt;b&gt;自动生成报告&lt;/b&gt;。助手决定的每一步都会实时显示在此处：选择的原因、工作位置以及发现的内容。</translation>
    </message>
    <message>
      <source>Tokens the run's model calls have used, and their cost estimated from the provider's list prices.</source>
      <translation>本次运行的模型调用已使用的 token 数，以及按服务商标价估算的费用。</translation>
    </message>
    <message>
      <source>{0} {1} done{2}</source>
      <translation>{0} {1} 完成{2}</translation>
    </message>
    <message>
      <source>Double-click to open the figure full size.</source>
      <extracomment>How a step's status is drawn; anything else is a failure.</extracomment>
      <translation>双击以全尺寸打开图件。</translation>
    </message>
    <message>
      <source>{0}
Click to show, double-click to open.</source>
      <translation>{0}
单击显示，双击打开。</translation>
    </message>
    <message>
      <source>written just now</source>
      <translation>刚刚写入</translation>
    </message>
    <message>
      <source>written {0} ago</source>
      <translation>{0}前写入</translation>
    </message>
    <message>
      <source>Read before the next decision</source>
      <translation>在下一次决策前阅读</translation>
    </message>
    <message>
      <source>Send note</source>
      <translation>发送备注</translation>
    </message>
    <message>
      <source>Pause after this step</source>
      <translation>此步骤后暂停</translation>
    </message>
    <message>
      <source>Tell {0} something while it works - e.g. use lambda 20, or leave the seismic line out</source>
      <translation>在 {0} 工作时向其发送指示，例如：使用 lambda 20，或不使用地震测线</translation>
    </message>
    <message>
      <source>Column (x)</source>
      <extracomment>The colour map array viewers open with, a pyqtgraph gradient preset. Emitted on a left click in pick mode: (col, row, value). Emitted once a second profile point is set: ([col1, row1], [col2, row2]). Emitted when the first point of a new profile is clicked: [col, row]. Emitted when the "Clear profile" button removes the profile. Profile drawing as the page set it, given back when picking stops. (value label, log) of the array on screen: what quantity it is. The levels the viewer (or the page, via set_levels) would draw with, in display units (log10 for a log display). Set while the viewer moves the levels itself, so the colour bar's level signals are not read back as the user dragging them.</extracomment>
      <translation>列 (x)</translation>
    </message>
    <message>
      <source>Row (y)</source>
      <translation>行 (y)</translation>
    </message>
    <message>
      <source>x(col): {0}, y(row): {1}, {2}</source>
      <translation>x(列)：{0}，y(行)：{1}，{2}</translation>
    </message>
    <message>
      <source>Export view as PNG</source>
      <translation>将视图导出为 PNG</translation>
    </message>
    <message>
      <source>Load</source>
      <translation>载入</translation>
    </message>
    <message>
      <source>Templates…</source>
      <translation>模板…</translation>
    </message>
    <message>
      <source>Write the column templates, each with an example row, to a folder.</source>
      <translation>将列模板（各带一行示例）写入文件夹。</translation>
    </message>
    <message>
      <source>Remove every well, log and water level.</source>
      <translation>移除所有钻孔、测井曲线和水位。</translation>
    </message>
    <message>
      <source>Wells</source>
      <translation>钻孔</translation>
    </message>
    <message>
      <source>Lithology</source>
      <translation>岩性</translation>
    </message>
    <message>
      <source>Water levels</source>
      <translation>水位</translation>
    </message>
    <message>
      <source>Geophysical logs</source>
      <translation>地球物理测井曲线</translation>
    </message>
    <message>
      <source>Add row</source>
      <translation>添加行</translation>
    </message>
    <message>
      <source>Remove row</source>
      <translation>删除行</translation>
    </message>
    <message>
      <source>Lithology legend</source>
      <translation>岩性图例</translation>
    </message>
    <message>
      <source>Double-click a colour to change it; edit a label to rename it in the legend.</source>
      <translation>双击颜色进行更改；编辑标签可重命名图例中的名称。</translation>
    </message>
    <message>
      <source>Load {0}</source>
      <translation>载入 {0}</translation>
    </message>
    <message>
      <source>Write borehole templates to</source>
      <translation>钻孔模板写入至</translation>
    </message>
    <message>
      <source>Lock range</source>
      <extracomment>The limits to draw with changed: locked or unlocked, or a limit typed while locked.</extracomment>
      <translation>锁定范围</translation>
    </message>
    <message>
      <source>Keep {0} on the limits typed beside this instead of rescaling to each plot. Two surveys, time steps or lines can only be compared on one scale. Unticked, the boxes show the limits in use, so ticking it keeps what is on screen.</source>
      <translation>将 {0} 固定在旁边输入的范围内，而不是随每幅图自动缩放。两次测量、时间步或测线只有在同一刻度下才能比较。未勾选时，输入框显示当前使用的范围，因此勾选后会保持屏幕上的显示。</translation>
    </message>
    <message>
      <source>{0} colour limit, used while “Lock range” is ticked.</source>
      <translation>{0}色标界限，勾选“锁定范围”时使用。</translation>
    </message>
    <message>
      <source>Reverse the colour map, so the colours run the other way along the colour bar.</source>
      <extracomment>Maps for a quantity read from low to high. ``Spectral_r`` is the ERT convention and stays in this group, where the resistivity views look for it. Maps for a signed quantity read either side of a centre value. The seismic gather's own blue-white-red: nearly white over the middle 4 % so the zero crossings stay quiet and only the arrivals carry colour. It is not a matplotlib map, so it is built here, and offered by the view that uses it. Maps defined here rather than by matplotlib: name -&gt; (stops, RGBA bytes, label). ERT resistivity sections time-lapse % change from the baseline ERT coverage (log10 sensitivity) the ERT QC pseudosection seismic velocity sections and volumes a shot gather's amplitude image EM resistivity: sections, volume, slices the EM survey QC station map gravity / magnetic anomaly maps gravity density-contrast models magnetic susceptibility models ground-penetrating radar radargrams Project Map plan layers hydrological model maps a saved 2-D array a 3-D volume read from a file mesh region markers survey layouts and pseudo-depth points How a tooltip names each key: "resistivity sections", ... PyVista takes the same as matplotlib. The full map name - ``viridis``, ``viridis_r`` - after the user picked one, or after another page changed the shared choice while this one was hidden.</extracomment>
      <translation>反转色标，使颜色沿色标条反向排列。</translation>
    </message>
    <message>
      <source>Colour map for {0}: {1}{2}.
Remembered for this session and shared by every view of {3}; a figure exported from the view uses it too.</source>
      <translation>{0} 的色标：{1}{2}。
在本次会话中保留，并由 {3} 的所有视图共享；从视图导出的图件也使用该色标。</translation>
    </message>
    <message>
      <source>log x</source>
      <extracomment>Emitted on a left click near a curve: (x, y).</extracomment>
      <translation>对数 x</translation>
    </message>
    <message>
      <source>log y</source>
      <translation>对数 y</translation>
    </message>
    <message>
      <source>pick</source>
      <translation>拾取</translation>
    </message>
    <message>
      <source>Export curves as CSV</source>
      <translation>将曲线导出为 CSV</translation>
    </message>
    <message>
      <source>Export plot as PNG</source>
      <translation>将图件导出为 PNG</translation>
    </message>
    <message>
      <source>Show dropped gates</source>
      <extracomment>How each verdict is drawn, as verdict -&gt; (colour, symbol, filled). Kept gates are the only filled ones, so the picture reads before the legend does. Per-moment line colour for the modelled response. A gate the loader kept and the inversion then threw out. Drawn over the kept marker rather than replacing it, because both facts are true of that gate and the second one only exists once a fit has run.</extracomment>
      <translation>显示已剔除时窗</translation>
    </message>
    <message>
      <source>Draw the gates the current selection removes, each marked with the test that removed it. Turning this off leaves the gates the inversion will actually see.</source>
      <translation>绘制当前选择所剔除的时窗，并标注剔除它的检验项。关闭后仅显示反演实际使用的时窗。</translation>
    </message>
    <message>
      <source>Gate windows</source>
      <translation>时窗区间</translation>
    </message>
    <message>
      <source>Draw each gate as a bar from its open time to its close time. The response is integrated across that width, so a late gate averages over a span comparable to its own centre time.</source>
      <translation>将每个时窗绘制为从开启时间到关闭时间的条带。响应在该宽度上积分，因此晚期时窗的平均跨度与其自身中心时间相当。</translation>
    </message>
    <message>
      <source>|dB/dt| (V)</source>
      <translation>|dB/dt| (V)</translation>
    </message>
    <message>
      <source>Export gates as CSV</source>
      <translation>将时窗导出为 CSV</translation>
    </message>
    <message>
      <source>rejected by hand</source>
      <translation>人工剔除</translation>
    </message>
    <message>
      <source>Which survey line to section. Lines are sectioned one at a time because their along-line distances are not continuous with each other; 'All lines' chains them and marks the joins.</source>
      <extracomment>Colours shared with the acquisition-software convention: every sounding in black, the line being sectioned in red, its zero-distance end in blue. Smallest map extent along one axis, as a fraction of the other, so a survey run along a single easting or northing still draws as a map. Figure size the current layout was computed for, so a resize event that carries no change does not schedule the work again. Drawing can itself emit a resize event, and without this the two feed each other.</extracomment>
      <translation>要生成断面的测线。由于各测线的沿线距离彼此不连续，断面逐条生成；“全部测线”会将其首尾相接并标出接合处。</translation>
    </message>
    <message>
      <source>Basemap</source>
      <translation>底图</translation>
    </message>
    <message>
      <source>Draw map tiles under the soundings. Tiles are fetched once and cached on disk, so a line already looked at stays available offline. Needs the survey's longitude/latitude, which a TEMcompany project carries; the axes stay in projected metres, so distances are unaffected.</source>
      <translation>在测深下方绘制地图瓦片。瓦片只获取一次并缓存到磁盘，因此已查看过的测线离线时仍可用。需要测量的经纬度（TEMcompany 工程包含此信息）；坐标轴仍为投影米制，距离不受影响。</translation>
    </message>
    <message>
      <source>Width of the map column, against the section beside it. Scrolling over either panel zooms it about the cursor, dragging pans, and a double-click returns to the whole survey.</source>
      <translation>地图栏相对于旁边断面的宽度。在任一面板上滚动以光标为中心缩放，拖动可平移，双击返回整个测区。</translation>
    </message>
    <message>
      <source>DOI: {0}</source>
      <translation>DOI：{0}</translation>
    </message>
    <message>
      <source>How the cells below the depth of investigation are drawn. Below that depth, changing the whole remaining column by one decade in resistivity moves the predicted response by less than the threshold beside this control, measured in the gates' own error bars.

Fade draws them washed out, so the section stays continuous and the regularized part is still distinguishable. Hide leaves them blank. Show draws them at full strength, with the depth-of-investigation line marking where they begin.</source>
      <translation>探测深度以下单元的绘制方式。在该深度以下，将剩余整列的电阻率改变一个数量级，预测响应的变化小于此控件旁的阈值（以各时窗自身的误差棒度量）。

“渐隐”将其淡化绘制，使断面保持连续，同时仍可区分受正则化控制的部分。“隐藏”将其置空。“显示”以完整强度绘制，并用探测深度线标出其起始位置。</translation>
    </message>
    <message>
      <source>Smooth interpolates the recovered models between soundings and down each layer stack, so the section reads continuously rather than as a grid of blocks. It adds no resolution, and the exported model is unchanged.

Layer cells draws one rectangle per layer per sounding, which is what the inversion solved for.</source>
      <translation>“平滑”在测深之间及沿各层序向下插值恢复的模型，使断面连续显示而非块状网格。它不增加分辨率，导出的模型也不变。

“层单元”为每个测深的每一层绘制一个矩形，即反演实际求解的内容。</translation>
    </message>
    <message>
      <source>Depth measures from each sounding's own ground surface, so the section is flat-topped and layers line up by burial depth.

Elevation hangs every sounding from its recorded ground level, so the top of the section is the topography and a flat-lying unit reads as flat. Available when the survey carries elevations. The inversion is unchanged either way, since each 1D model is solved under its own station.</source>
      <translation>深度从各测深自身的地面起算，因此断面顶部平直，各层按埋深对齐。

高程将每个测深挂在其记录的地面高程上，因此断面顶部即地形，水平产出的地层显示为水平。测量带有高程时可用。两种方式下反演结果不变，因为每个一维模型都在其自身测点下求解。</translation>
    </message>
    <message>
      <source>Cumulated sensitivity a depth must carry to count as investigated. S is the sum, over every layer at and below that depth, of how far the predicted response moves when the layer changes by one e-fold in resistivity, measured in error bars. The definition follows Christiansen and Auken (2012).

Higher values put the depth of investigation shallower and shorten the section; lower values extend it deeper. The value carries no units, so one setting applies across systems.</source>
      <translation>某一深度被视为已探测所需达到的累积灵敏度。S 为该深度及其以下各层的累加值，每层的贡献为该层电阻率变化一个 e 倍时预测响应的变化量（以误差棒为单位）。定义参照 Christiansen 和 Auken (2012)。

取值越高，探测深度越浅，断面越短；取值越低，探测深度越深。该值无量纲，因此同一设置可适用于不同系统。</translation>
    </message>
    <message>
      <source>No ground elevations for these soundings, or the survey is flat to within 5 cm, so depth and elevation would draw the same section. A TEM project records an elevation per station.</source>
      <translation>这些测深没有地面高程，或测区起伏在 5 cm 以内，因此按深度和按高程绘制的断面相同。TEM 工程会为每个测点记录高程。</translation>
    </message>
    <message>
      <source>This project's longitude/latitude and its projected coordinates do not place the soundings in the same spot, so imagery cannot be registered to the survey. The section is unaffected: it is drawn from the projected coordinates alone.</source>
      <translation>本工程的经纬度与投影坐标给出的测深位置不一致，因此影像无法与测量配准。断面不受影响：它仅依据投影坐标绘制。</translation>
    </message>
    <message>
      <source>No longitude/latitude for these soundings, so map tiles cannot be placed. A TEMcompany project folder carries them.</source>
      <translation>这些测深没有经纬度，无法放置地图瓦片。TEMcompany 工程文件夹中包含经纬度。</translation>
    </message>
    <message>
      <source>Line {0}</source>
      <translation>测线 {0}</translation>
    </message>
    <message>
      <source>Northing − {0:,.0f} {1}</source>
      <extracomment>Opacity of the part of the model the data do not resolve.</extracomment>
      <translation>北坐标 − {0:,.0f} {1}</translation>
    </message>
    <message>
      <source>Survey map</source>
      <translation>测量地图</translation>
    </message>
    <message>
      <source>Colour by:</source>
      <extracomment>Columns of the station table, as (heading, row key, format). What the map can colour stations by, as (label, row key). The colour fields that are lengths in metres, whose range the map's title gives in the studio's length unit. Rows whose bare value invites the wrong reading. The tree shows a field name and a number with none of the surrounding argument, so the few fields where that is not enough carry the argument as a tooltip. Emitted with the 0-based sounding index of a station the user picked. Set while the table is being rebuilt, so that clearing and refilling it does not read back as the user picking a station.</extracomment>
      <translation>着色依据：</translation>
    </message>
    <message>
      <source>What the gate selection above the plot keeps, over the whole survey. A station whose every gate is dropped disappears from the inversion entirely, so it is counted separately.</source>
      <translation>图上方的时窗选择在整个测量中保留的内容。所有时窗均被剔除的测点将完全不参与反演，因此单独计数。</translation>
    </message>
    <message>
      <source>Field</source>
      <translation>字段</translation>
    </message>
    <message>
      <source>Value</source>
      <translation>值</translation>
    </message>
    <message>
      <source>Line:</source>
      <translation>测线：</translation>
    </message>
    <message>
      <source>Which survey line to draw. Distance runs from that line's own first station.</source>
      <translation>要绘制的测线。距离从该测线自身的第一个测点起算。</translation>
    </message>
    <message>
      <source>Smoothing:</source>
      <translation>平滑：</translation>
    </message>
    <message>
      <source> stations</source>
      <translation> 个测点</translation>
    </message>
    <message>
      <source>Width of a running mean over stations. Cosmetic: the station-to-station scatter obscures the trend this is drawn to show. Set it to 1 to plot the values themselves.</source>
      <translation>沿测点滑动平均的窗口宽度。仅影响显示：测点间的离散会掩盖要展示的趋势。设为 1 则绘制原始值。</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0}&lt;/b&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;{1}</source>
      <translation>&lt;b&gt;{0}&lt;/b&gt;&amp;nbsp;&amp;nbsp;&amp;nbsp;{1}</translation>
    </message>
    <message>
      <source>Gravity / Magnetics</source>
      <translation>重力 / 磁法</translation>
    </message>
    <message>
      <source>Product to add</source>
      <translation>要添加的产品</translation>
    </message>
    <message>
      <source>Joint result</source>
      <translation>联合结果</translation>
    </message>
    <message>
      <source>Model to add</source>
      <translation>要添加的模型</translation>
    </message>
    <message>
      <source>Add result to Project Map</source>
      <translation>将结果添加到工程地图</translation>
    </message>
    <message>
      <source>Save a map snapshot in this project. Source results stay unchanged.
Profile elevation is not a map coordinate. Confirm the survey location below.</source>
      <translation>在此工程中保存地图快照。源结果保持不变。
剖面高程不是地图坐标。请在下方确认测量位置。</translation>
    </message>
    <message>
      <source>Coordinates carried by this result</source>
      <translation>此结果携带的坐标</translation>
    </message>
    <message>
      <source>Straight line: start + bearing</source>
      <translation>直线：起点 + 方位角</translation>
    </message>
    <message>
      <source>CSV control points: distance,x,y</source>
      <translation>CSV 控制点：distance,x,y</translation>
    </message>
    <message>
      <source>CSV positions: x,y (one row per sample)</source>
      <translation>CSV 位置：x,y（每个采样一行）</translation>
    </message>
    <message>
      <source>Location</source>
      <translation>位置</translation>
    </message>
    <message>
      <source>Coordinate system</source>
      <translation>坐标系</translation>
    </message>
    <message>
      <source>LOCAL = shared project coordinates in metres (no basemap).
EPSG:4326 = longitude, latitude. Or enter the survey EPSG code.
Start + bearing needs a projected metre CRS or LOCAL.</source>
      <translation>LOCAL = 以米为单位的共享工程坐标（无底图）。
EPSG:4326 = 经度、纬度。也可输入测量所用的 EPSG 代码。
起点 + 方位角需要以米为单位的投影 CRS 或 LOCAL。</translation>
    </message>
    <message>
      <source>° clockwise from north</source>
      <translation>°（自北顺时针）</translation>
    </message>
    <message>
      <source>Start X at distance {0:g} m</source>
      <translation>X 起点位于距离 {0:g} m 处</translation>
    </message>
    <message>
      <source>Start Y</source>
      <translation>起始 Y</translation>
    </message>
    <message>
      <source>Bearing</source>
      <translation>方位角</translation>
    </message>
    <message>
      <source>Choose location CSV…</source>
      <translation>选择位置 CSV…</translation>
    </message>
    <message>
      <source>Add to Map</source>
      <translation>添加到地图</translation>
    </message>
    <message>
      <source>Survey location CSV</source>
      <translation>测量位置 CSV</translation>
    </message>
    <message>
      <source>Survey location</source>
      <translation>测量位置</translation>
    </message>
    <message>
      <source>Also draw the outer ("infinite") region: the coarse cells pyGIMLi appends around the parameter domain so the boundary condition sits far from the electrodes. They are part of the forward mesh but are never inverted, and they reach many times further than the section, so the view zooms out to show them.</source>
      <translation>同时绘制外部（“无限”）区域：pyGIMLi 在参数域周围附加的粗单元，使边界条件远离电极。它们属于正演网格但从不参与反演，且延伸范围远大于断面，因此视图将缩小以显示它们。</translation>
    </message>
    <message>
      <source>Cell edges</source>
      <translation>单元边</translation>
    </message>
    <message>
      <source>Draw the cell boundaries.</source>
      <translation>绘制单元边界。</translation>
    </message>
    <message>
      <source>Rebuild</source>
      <translation>重建</translation>
    </message>
    <message>
      <source>Build the mesh again from the current data and mesh settings. It is rebuilt on its own when this tab is opened after they change.</source>
      <translation>根据当前数据和网格设置重新构建网格。设置更改后打开此选项卡时会自动重建。</translation>
    </message>
    <message>
      <source>Cut open</source>
      <translation>剖开</translation>
    </message>
    <message>
      <source>Cut the inverted cells with a plane to see inside: drag the plane, or its arrow to turn it.</source>
      <translation>用平面切开反演单元以查看内部：拖动平面，或拖动其箭头以旋转。</translation>
    </message>
    <message>
      <source>Reset view</source>
      <translation>重置视图</translation>
    </message>
    <message>
      <source>A-priori zones</source>
      <translation>先验分区</translation>
    </message>
    <message>
      <source>Draw a polygon on the mesh and give it the resistivity known from a borehole, an excavation or another survey. The inversion starts from it; tick Fixed to keep the zone out of the inversion altogether.</source>
      <translation>在网格上绘制多边形，并赋予由钻孔、开挖或其他测量得知的电阻率。反演以此为起点；勾选“固定”可使该分区完全不参与反演。</translation>
    </message>
    <message>
      <source>Draw zone</source>
      <translation>绘制分区</translation>
    </message>
    <message>
      <source>Click on the mesh to place the vertices and click the first one again to close the polygon. Esc starts the polygon over; press the button again to stop without adding a zone.</source>
      <translation>在网格上点击放置顶点，再次点击第一个顶点以闭合多边形。按 Esc 重新开始绘制多边形；再次按下该按钮可停止且不添加分区。</translation>
    </message>
    <message>
      <source>Remove the selected zones.</source>
      <translation>移除所选分区。</translation>
    </message>
    <message>
      <source>Remove every zone.</source>
      <translation>移除所有分区。</translation>
    </message>
    <message>
      <source>Click to place vertices; click the first vertex to close. Esc starts over.</source>
      <translation>点击放置顶点；点击第一个顶点以闭合。按 Esc 重新开始。</translation>
    </message>
    <message>
      <source>Zones are drawn on a 2-D mesh. In a 3-D mesh they are boxes, set in the 3D Mesh Builder before the mesh is built.</source>
      <translation>分区在二维网格上绘制。在三维网格中分区为长方体，需在构建网格前于三维网格构建器中设置。</translation>
    </message>
    <message>
      <source>Zone</source>
      <translation>分区</translation>
    </message>
    <message>
      <source>Fixed</source>
      <translation>固定</translation>
    </message>
    <message>
      <source>Cells</source>
      <translation>单元</translation>
    </message>
    <message>
      <source>Double-click a name to rename the zone. Cells counts the cells of the parameter domain whose centre lies inside the polygon; where zones overlap, the one lower in the list takes the cell.</source>
      <translation>双击名称可重命名分区。“单元”统计中心位于多边形内的参数域单元数；分区重叠时，单元归列表中靠下的分区。</translation>
    </message>
    <message>
      <source>Mesh follows the zones</source>
      <translation>网格贴合分区</translation>
    </message>
    <message>
      <source>Build the mesh again so that the zone outlines become cell edges: no cell straddles an outline, so a zone's value - and a fixed zone - covers exactly the area drawn. The mesh is rebuilt after every zone you draw, move or remove; changing a zone's value leaves the mesh alone. Only the parts of an outline inside the inverted region are used. An outline meets the surface at the nearest surface node, and a vertex within a fifth of an electrode spacing of the surface or of a node is moved onto it, so no slivers of tiny cells form. Not available for an imported mesh.</source>
      <translation>重新构建网格，使分区轮廓成为单元边：没有单元跨越轮廓，因此分区的取值（以及固定分区）恰好覆盖所绘区域。每次绘制、移动或删除分区后都会重建网格；仅修改分区取值则不会重建。仅使用轮廓位于反演区域内的部分。轮廓在最近的地表节点处与地表相交；距地表或节点不足五分之一电极间距的顶点会被移到其上，以免形成细碎的微小单元。导入的网格不可用。</translation>
    </message>
    <message>
      <source>Sharp zone edges</source>
      <translation>锐利分区边界</translation>
    </message>
    <message>
      <source>Drop the smoothness constraint between cells on either side of a zone outline - between two zones, or a zone and the ground around it - so the inversion may put a sharp contrast there instead of smearing it out. Use it for a boundary known from a borehole, GPR or an excavation. The cell edges it cuts are drawn in black. Every engine honours it; rebuilding the mesh along the outlines makes the cut follow them exactly rather than the nearest cell edges.</source>
      <translation>取消分区轮廓两侧单元之间（两个分区之间，或分区与周围地层之间）的光滑度约束，使反演可在该处形成明显的电性差异而非将其抹平。适用于由钻孔、GPR 或开挖得知的边界。被切断的单元边以黑色绘制。所有引擎均支持；沿轮廓重建网格可使切断严格沿轮廓，而非沿最近的单元边。</translation>
    </message>
    <message>
      <source>The 3-D view could not draw this mesh: {0}</source>
      <translation>三维视图无法绘制此网格：{0}</translation>
    </message>
    <message>
      <source>Show mesh</source>
      <translation>显示网格</translation>
    </message>
    <message>
      <source>Overlay the inversion mesh cell boundaries.</source>
      <translation>叠加显示反演网格单元边界。</translation>
    </message>
    <message>
      <source>Off</source>
      <translation>关</translation>
    </message>
    <message>
      <source>Cells ×1</source>
      <translation>单元 ×1</translation>
    </message>
    <message>
      <source>Cells ×2</source>
      <translation>单元 ×2</translation>
    </message>
    <message>
      <source>Contour</source>
      <translation>等值线</translation>
    </message>
    <message>
      <source>How smoothly the model is drawn. “Cells” interpolates it onto a subdivided mesh and still draws cells; “Contour” draws filled contours on a regular grid instead, for the continuous image traditional resistivity software produces. Display only - no resolution is added and the exported model is unchanged. Turn “Show mesh” off to see the effect.

Contours cannot reproduce the soft per-cell sensitivity fade, so they draw the whole section: use “Hide below” or “Clean cut” to trim it to what the data resolve.</source>
      <translation>模型绘制的平滑程度。“单元”将模型插值到细分网格上，仍按单元绘制；“等值线”则在规则网格上绘制填充等值线，得到传统电阻率软件那样的连续图像。仅影响显示——不会提高分辨率，导出的模型也不变。关闭“显示网格”可查看效果。

等值线无法再现逐单元的灵敏度渐隐效果，因此会绘制整个断面：可使用“低于阈值隐藏”或“平滑裁切”将其裁剪到数据可分辨的范围。</translation>
    </message>
    <message>
      <source>levels </source>
      <translation>等级 </translation>
    </message>
    <message>
      <source>Number of filled contour bands. A high count reads as a continuous image; a low one bands the section, which is easier to read a value off but invents edges where the model is smooth.</source>
      <translation>填充等值线色带的数量。数量多时看起来像连续图像；数量少时断面呈分带显示，更便于读取数值，但会在模型光滑处制造虚假边界。</translation>
    </message>
    <message>
      <source>Smooth</source>
      <translation>平滑</translation>
    </message>
    <message>
      <source>Sensitivity</source>
      <translation>灵敏度</translation>
    </message>
    <message>
      <source>Draw the coverage (log10 cumulative sensitivity) instead of the model, so you can see which parts of the section the data actually constrain.</source>
      <translation>绘制覆盖度（log10 累积灵敏度）而非模型，以查看断面中哪些部分真正受数据约束。</translation>
    </message>
    <message>
      <source>Hide below</source>
      <translation>低于阈值隐藏</translation>
    </message>
    <message>
      <source>Blank the cells whose coverage falls under the threshold, rather than letting poorly constrained cells read as real structure. On by default; the line under the plot states the cut.</source>
      <translation>置空覆盖度低于阈值的单元，避免约束不足的单元被误读为真实结构。默认开启；图下方的说明会给出截断值。</translation>
    </message>
    <message>
      <source>Clean cut</source>
      <translation>平滑裁切</translation>
    </message>
    <message>
      <source>Clip the section to a smooth envelope at the coverage cut, instead of blanking cell by cell. The edge then follows how deep the survey sees rather than where the mesh happens to put a triangle. Needs “Hide below”.</source>
      <translation>在覆盖度截断处按平滑包络裁切断面，而不是逐单元置空。这样边缘反映的是测量的探测深度，而非网格三角形恰好所在的位置。需要启用“隐藏低于”。</translation>
    </message>
    <message>
      <source>Coverage cut in log10 units. The status line under the plot reports the range for the current result and how much of the section survives.</source>
      <translation>以 log10 为单位的覆盖度截断值。图下方的状态行会显示当前结果的范围以及断面保留的比例。</translation>
    </message>
    <message>
      <source>Rays</source>
      <translation>射线</translation>
    </message>
    <message>
      <source>Overlay the first-arrival ray paths. Where no ray passes, the velocity is regularization rather than data. Travel-time results only.</source>
      <translation>叠加显示初至射线路径。没有射线经过的位置，速度由正则化而非数据决定。仅适用于走时结果。</translation>
    </message>
    <message>
      <source>Hide uncovered</source>
      <translation>隐藏未覆盖区</translation>
    </message>
    <message>
      <source>Blank the cells no ray passes through. Their velocity comes from the regularization pulling on neighbours, not from the travel times, so showing them invites reading structure into the smoothing. Untick to see the full inverted domain.</source>
      <translation>置空没有射线穿过的单元。这些单元的速度来自正则化对相邻单元的约束，而非走时，显示它们容易将平滑效应误读为结构。取消勾选可查看完整反演区域。</translation>
    </message>
    <message>
      <source>Freeze the colour limits instead of rescaling to each result. Time steps can only be compared on one scale; without this, every step is stretched to its own min/max and the change between them cannot be read off the colours.</source>
      <translation>冻结色阶范围，而不针对每个结果重新缩放。各时间步只有在同一色阶下才能比较；否则每一步都会拉伸到其自身的最小/最大值，无法从颜色读出它们之间的变化。</translation>
    </message>
    <message>
      <source>{0} colour limit, applied when “Lock range” is ticked. While it is unticked these track the result on screen, so ticking the box keeps what you see.</source>
      <translation>{0}色标界限，勾选“锁定范围”时生效。未勾选时，这些值跟随屏幕上的结果变化，因此勾选后会保持当前所见的范围。</translation>
    </message>
    <message>
      <source>Physical property or categorical labels to display</source>
      <translation>要显示的物性或分类标签</translation>
    </message>
    <message>
      <source>Open a model to inspect its 3D properties here.</source>
      <translation>打开模型以在此查看其三维属性。</translation>
    </message>
    <message>
      <source>Clip plane (drag to inspect the interior)</source>
      <translation>裁切平面（拖动以查看内部）</translation>
    </message>
    <message>
      <source>Interactive 3D view is unavailable in this session.&lt;br&gt;&lt;code&gt;{0}&lt;/code&gt;&lt;br&gt;&lt;br&gt;If pyvista is missing, install the 3D viewers with &lt;code&gt;pip install "pyhydrogeophysx[desktop-3d]"&lt;/code&gt;. Check &lt;code&gt;conda list numpy&lt;/code&gt; first: a conda channel there means this environment's packages are conda-managed, so use &lt;code&gt;conda install -c conda-forge pyvista pyvistaqt&lt;/code&gt; instead.&lt;br&gt;&lt;br&gt;The generated figures and files remain available in the next tab.</source>
      <translation>本会话中无法使用交互式三维视图。&lt;br&gt;&lt;code&gt;{0}&lt;/code&gt;&lt;br&gt;&lt;br&gt;如果缺少 pyvista，请使用 &lt;code&gt;pip install "pyhydrogeophysx[desktop-3d]"&lt;/code&gt; 安装三维查看器。请先检查 &lt;code&gt;conda list numpy&lt;/code&gt;：若其中显示 conda 渠道，说明该环境的包由 conda 管理，此时应改用 &lt;code&gt;conda install -c conda-forge pyvista pyvistaqt&lt;/code&gt;。&lt;br&gt;&lt;br&gt;生成的图件和文件仍可在下一个选项卡中查看。</translation>
    </message>
    <message>
      <source>Slice</source>
      <translation>切片</translation>
    </message>
    <message>
      <source>Drag the clipping plane to inspect the model interior.</source>
      <translation>拖动裁切平面以查看模型内部。</translation>
    </message>
    <message>
      <source>3D volume file not found: &lt;code&gt;{0}&lt;/code&gt;</source>
      <translation>未找到 3D 体数据文件：&lt;code&gt;{0}&lt;/code&gt;</translation>
    </message>
    <message>
      <source>3D volume saved at &lt;code&gt;{0}&lt;/code&gt;. Use the Figures &amp; files tab in this session.</source>
      <translation>3D 体数据已保存至 &lt;code&gt;{0}&lt;/code&gt;。请在本会话的“图件与文件”选项卡中查看。</translation>
    </message>
    <message>
      <source>Could not display &lt;code&gt;{0}&lt;/code&gt;: {1}</source>
      <translation>无法显示 &lt;code&gt;{0}&lt;/code&gt;：{1}</translation>
    </message>
    <message>
      <source>{0}: interactive 3D is unavailable in this session.</source>
      <translation>{0}：本会话中交互式三维不可用。</translation>
    </message>
    <message>
      <source>&lt;b&gt;{0}&lt;/b&gt; · scalar: {1} · drag to rotate, wheel to zoom</source>
      <translation>&lt;b&gt;{0}&lt;/b&gt; · 标量：{1} · 拖动旋转，滚轮缩放</translation>
    </message>
    <message>
      <source>Linked sections &amp;&amp; values</source>
      <translation>关联断面 &amp;&amp; 数值</translation>
    </message>
    <message>
      <source>Interactive 3D is unavailable · physical-coordinate sections remain available</source>
      <translation>交互式三维不可用 · 物理坐标断面仍可用</translation>
    </message>
    <message>
      <source>Clip plane (drag to slice)</source>
      <translation>裁切平面（拖动以切片）</translation>
    </message>
    <message>
      <source>Y position</source>
      <translation>Y 位置</translation>
    </message>
    <message>
      <source>Resistivity section</source>
      <translation>电阻率断面</translation>
    </message>
    <message>
      <source>{0} section</source>
      <translation>{0} 断面</translation>
    </message>
    <message>
      <source>Mask</source>
      <extracomment>Colour map by parameter name; others use the default.</extracomment>
      <translation>遮罩</translation>
    </message>
    <message>
      <source>Blank what the data do not constrain; the caption says by what.</source>
      <translation>置空数据未约束的区域；说明中会注明依据。</translation>
    </message>
    <message>
      <source>z slice </source>
      <translation>z 切片 </translation>
    </message>
    <message>
      <source>Parameter</source>
      <translation>参数</translation>
    </message>
    <message>
      <source>Export figure…</source>
      <translation>导出图件…</translation>
    </message>
    <message>
      <source>Save the section as a report figure: PDF (vector, fonts embedded) or 300 dpi PNG, with units, colour bar, scale bar and the mask's basis.</source>
      <translation>将断面保存为报告图件：PDF（矢量，内嵌字体）或 300 dpi PNG，含单位、色标、比例尺及遮罩依据。</translation>
    </message>
    <message>
      <source>Export figure</source>
      <translation>导出图件</translation>
    </message>
    <message>
      <source>PDF figure (*.pdf);;PNG image (*.png)</source>
      <translation>PDF 图件 (*.pdf);;PNG 图像 (*.png)</translation>
    </message>
    <message>
      <source>Could not export the figure: {0}</source>
      <translation>无法导出图件：{0}</translation>
    </message>
    <message>
      <source>Saved {0}</source>
      <translation>已保存 {0}</translation>
    </message>
    <message>
      <source>Masked: {0}.</source>
      <translation>已遮罩：{0}。</translation>
    </message>
    <message>
      <source>Unmasked; the default mask would apply: {0}.</source>
      <translation>未遮罩；默认遮罩将为：{0}。</translation>
    </message>
    <message>
      <source>No coverage, DOI or resolution with this result: every cell is shown.</source>
      <translation>该结果没有覆盖度、DOI 或分辨率信息：显示所有单元。</translation>
    </message>
    <message>
      <source>slice {0} of {1}</source>
      <translation>切片 {0} / {1}</translation>
    </message>
    <message>
      <source>depth [m]</source>
      <translation>深度 [m]</translation>
    </message>
    <message>
      <source>log10 value</source>
      <translation>log10 值</translation>
    </message>
    <message>
      <source>value</source>
      <translation>值</translation>
    </message>
    <message>
      <source>distance [m]</source>
      <translation>距离 [m]</translation>
    </message>
    <message>
      <source>Resistivity at depth {0}</source>
      <translation>深度 {0} 处的电阻率</translation>
    </message>
    <message>
      <source>Depth {0}</source>
      <translation>深度 {0}</translation>
    </message>
    <message>
      <source>For example: Site A 2026</source>
      <extracomment>Characters Windows refuses in a folder name, and the names it reserves.</extracomment>
      <translation>例如：场地 A 2026</translation>
    </message>
    <message>
      <source>Name</source>
      <translation>名称</translation>
    </message>
    <message>
      <source>Don't ask again</source>
      <translation>不再询问</translation>
    </message>
    <message>
      <source>Keep using the default folder without asking. File › New Project… still makes a project.</source>
      <translation>继续使用默认文件夹，不再询问。“文件 › 新建工程…”仍可创建工程。</translation>
    </message>
    <message>
      <source>Use Default Folder</source>
      <translation>使用默认文件夹</translation>
    </message>
    <message>
      <source>Create Project</source>
      <translation>创建工程</translation>
    </message>
    <message>
      <source>Choose where to keep the project</source>
      <translation>选择工程保存位置</translation>
    </message>
    <message>
      <source>Creates {0}
This path has characters Windows' code page cannot show. Runs still work, but mesh files are written through a temporary folder, which is slower.</source>
      <translation>将创建 {0}
此路径包含 Windows 代码页无法显示的字符。运行仍可进行，但网格文件将经由临时文件夹写入，速度较慢。</translation>
    </message>
    <message>
      <source>Creates {0}</source>
      <translation>将创建 {0}</translation>
    </message>
    <message>
      <source>Run ID: {0}
Folder: {1}</source>
      <translation>运行 ID：{0}
文件夹：{1}</translation>
    </message>
    <message>
      <source>Discard</source>
      <translation>放弃</translation>
    </message>
    <message>
      <source>Delete these runs' folders.</source>
      <translation>删除这些运行的文件夹。</translation>
    </message>
    <message>
      <source>No inversion run yet.</source>
      <translation>尚未运行反演。</translation>
    </message>
    <message>
      <source>{0}&lt;span style='font-size:13px'&gt;{1}&lt;/span&gt;&lt;br&gt;&lt;span style='color:{2}'&gt;&lt;b&gt;{3}&lt;/b&gt;&lt;/span&gt;{4}</source>
      <translation>{0}&lt;span style='font-size:13px'&gt;{1}&lt;/span&gt;&lt;br&gt;&lt;span style='color:{2}'&gt;&lt;b&gt;{3}&lt;/b&gt;&lt;/span&gt;{4}</translation>
    </message>
    <message>
      <source>Iteration (all recorded solves)</source>
      <translation>迭代（所有已记录的求解）</translation>
    </message>
    <message>
      <source>Weighted convergence</source>
      <translation>加权收敛</translation>
    </message>
    <message>
      <source>Iteration (all stages, in order)</source>
      <translation>迭代（按顺序的所有阶段）</translation>
    </message>
    <message>
      <source>Convergence</source>
      <translation>收敛</translation>
    </message>
    <message>
      <source>Misfit per {0}</source>
      <translation>每 {0} 拟合差</translation>
    </message>
    <message>
      <source>Iteration</source>
      <translation>迭代</translation>
    </message>
    <message>
      <source>Final data misfit</source>
      <translation>最终数据拟合差</translation>
    </message>
    <message>
      <source>&lt;span style='color:#8e8e93'&gt;Run an inversion to see its quality (χ², RMS, convergence) here.&lt;/span&gt;</source>
      <translation>&lt;span style='color:#8e8e93'&gt;运行反演后，此处将显示其质量（χ²、RMS、收敛情况）。&lt;/span&gt;</translation>
    </message>
    <message>
      <source>How this run fitted its error model; fixed once it ran.</source>
      <translation>本次运行拟合误差模型的方式；运行后即固定。</translation>
    </message>
    <message>
      <source>Fit to</source>
      <translation>拟合目标</translation>
    </message>
    <message>
      <source>Ohms  (|dR|)</source>
      <translation>欧姆  (|dR|)</translation>
    </message>
    <message>
      <source>Percent of the resistance</source>
      <translation>电阻的百分比</translation>
    </message>
    <message>
      <source>Draw each pair's disagreement in ohms, as the model is fitted, or as a percentage of its resistance - the number the reciprocal-error limit under More checks and a data error in percent are compared with. The model is the same either way.</source>
      <translation>以欧姆（与模型拟合时相同）或占其电阻的百分比绘制每对测量的差异——后者即“更多”中互易误差限值和百分比数据误差所比较的数值。两种方式下模型相同。</translation>
    </message>
    <message>
      <source>Error as</source>
      <translation>误差表示为</translation>
    </message>
    <message>
      <source>Pairs the filter left out</source>
      <translation>滤波剔除的配对</translation>
    </message>
    <message>
      <source>Draw, in grey, the pairs the fit does not use.</source>
      <translation>以灰色绘制拟合未使用的测量对。</translation>
    </message>
    <message>
      <source>Colour by survey</source>
      <translation>按测量着色</translation>
    </message>
    <message>
      <source>Colour a time-lapse series' pairs from the first survey to the last, or draw them in one colour.</source>
      <translation>按从第一次到最后一次测量为时移序列的测量对着色，或以单一颜色绘制。</translation>
    </message>
    <message>
      <source>Use for the data errors</source>
      <translation>用作数据误差</translation>
    </message>
    <message>
      <source>Take the next inversion's data errors from this model: under Data errors, the source becomes “From the reciprocal error model”.</source>
      <translation>下次反演的数据误差取自此模型：在“数据误差”下，来源变为“来自互易误差模型”。</translation>
    </message>
    <message>
      <source>Save figure and pairs…</source>
      <translation>保存图件和数据对…</translation>
    </message>
    <message>
      <source>Save the figure as it is drawn, and every pair beside it as a CSV table with the model in its header.</source>
      <translation>按当前绘制效果保存图件，并将每个数据对另存为 CSV 表格，表头中包含模型信息。</translation>
    </message>
    <message>
      <source>The next inversion takes its data errors from this model.</source>
      <translation>下次反演的数据误差取自此模型。</translation>
    </message>
    <message>
      <source>The next inversion does not use this model: its data errors come from the source chosen under Data errors.</source>
      <translation>下次反演不使用此模型：其数据误差来自“数据误差”下所选的来源。</translation>
    </message>
    <message>
      <source>Pairs the filter left out ({0:,})</source>
      <translation>滤波剔除的配对 ({0:,})</translation>
    </message>
    <message>
      <source>Save the reciprocal error figure</source>
      <translation>保存互易误差图</translation>
    </message>
    <message>
      <source>Saved {0} and {1} in {2}.</source>
      <translation>已将 {0} 和 {1} 保存到 {2}。</translation>
    </message>
    <message>
      <source>Stacked section: the result.
Velocity check: is the stacking velocity right?
Flat-event check: is an event a reflection, or left over from the mutes?</source>
      <translation>叠加断面：结果。
速度检查：叠加速度是否正确？
平同相轴检查：该同相轴是反射，还是切除残留？</translation>
    </message>
    <message>
      <source>Depth converts two-way time with the stacking velocity, so it is only as right as that velocity.</source>
      <translation>深度由双程时间按叠加速度换算，其准确性取决于该速度。</translation>
    </message>
    <message>
      <source>Display</source>
      <translation>显示</translation>
    </message>
    <message>
      <source>Two-way time (ms)</source>
      <translation>双程时间 (ms)</translation>
    </message>
    <message>
      <source>Stacking velocity (m/s)</source>
      <translation>叠加速度 (m/s)</translation>
    </message>
    <message>
      <source>{0:.0f} m/s, {1:.1f} ms, semblance {2:.2f}</source>
      <translation>{0:.0f} m/s，{1:.1f} ms，相似系数 {2:.2f}</translation>
    </message>
    <message>
      <source>offset {0}, {1:.1f} ms</source>
      <translation>偏移距 {0}，{1:.1f} ms</translation>
    </message>
    <message>
      <source>position {0}, {1}, {2} traces</source>
      <translation>位置 {0}，{1}，{2} 道</translation>
    </message>
    <message>
      <source>End the running computation now. Nothing it computed so far is kept; run it again to start over.</source>
      <translation>立即结束正在运行的计算。已计算的内容不会保留；需重新运行以从头开始。</translation>
    </message>
    <message>
      <source>REPLAY</source>
      <extracomment>The file a run's recording is saved as, in its output folder. Longest pause between two recorded calls on the replay's timeline, seconds.</extracomment>
      <translation>回放</translation>
    </message>
    <message>
      <source>Play</source>
      <translation>播放</translation>
    </message>
    <message>
      <source>The run's own clock: how long it had been running at this point.</source>
      <translation>运行自身的计时：到此时已运行的时长。</translation>
    </message>
    <message>
      <source>Save frame</source>
      <translation>保存画面</translation>
    </message>
    <message>
      <source>Save the Live tab as it looks now, as a PNG in the run's folder.</source>
      <translation>将“实时”选项卡的当前画面保存为 PNG，存放在运行文件夹中。</translation>
    </message>
    <message>
      <source>Close replay</source>
      <translation>关闭回放</translation>
    </message>
    <message>
      <source>Pause</source>
      <translation>暂停</translation>
    </message>
    <message>
      <source>{0}: {1:.6g} {2} · E {3:,.3f}, N {4:,.3f}, Z {5:,.3f} m · Z is elevation, not depth</source>
      <translation>{0}：{1:.6g} {2} · E {3:,.3f}，N {4:,.3f}，Z {5:,.3f} m · Z 为高程，而非深度</translation>
    </message>
    <message>
      <source>A: {0}
B: {1}
Same grid · shared scale · difference B − A · no resampling</source>
      <translation>A：{0}
B：{1}
同一网格 · 共用色阶 · 差值 B − A · 不重采样</translation>
    </message>
    <message>
      <source>Wiggle/N</source>
      <translation>波形/N</translation>
    </message>
    <message>
      <source>Truncate the time axis (e.g. to the longest first arrival).</source>
      <translation>截断时间轴（例如截至最晚的初至）。</translation>
    </message>
    <message>
      <source>Auto</source>
      <translation>自动</translation>
    </message>
    <message>
      <source>Auto-fit the time window to the first arrivals.</source>
      <translation>根据初至自动调整时间窗口。</translation>
    </message>
    <message>
      <source>Max time</source>
      <translation>最大时间</translation>
    </message>
    <message>
      <source>Sample</source>
      <translation>样本</translation>
    </message>
    <message>
      <source> smp</source>
      <translation> 采样点</translation>
    </message>
    <message>
      <source>trace: -, time: -, amp: -</source>
      <translation>道：-，时间：-，振幅：-</translation>
    </message>
    <message>
      <source>trace: {0}, time: {1:.4g} {2}, amp: {3:.3g}</source>
      <translation>道：{0}，时间：{1:.4g} {2}，振幅：{3:.3g}</translation>
    </message>
    <message>
      <source>Which survey of the series is displayed.</source>
      <translation>显示序列中的哪一期测量。</translation>
    </message>
    <message>
      <source>Previous survey</source>
      <translation>上一次勘探</translation>
    </message>
    <message>
      <source>Next survey</source>
      <translation>下一个测量</translation>
    </message>
    <message>
      <source>Absolute model, or its change from the first survey. The change is what a monitoring survey is run to see: it cancels the static structure both surveys share and leaves what moved.</source>
      <translation>绝对模型，或相对于第一次测量的变化。变化正是监测测量所要观察的：它消除两次测量共有的静态结构，只留下发生变化的部分。</translation>
    </message>
    <message>
      <source>Report every time step at one reference temperature, so the change between surveys is moisture rather than the seasonal warming and cooling of the ground (about 2 % of resistivity per degC).</source>
      <extracomment>A validated correction spec, when the user presses Apply. The user asked for the inverted models back.</extracomment>
      <translation>将每个时间步统一校正到同一参考温度，使各次测量之间的变化反映含水量变化，而非地温的季节性升降（每 °C 约影响电阻率 2 %）。</translation>
    </message>
    <message>
      <source>Temperature the corrected sections are reported at. 25 °C is the laboratory convention petrophysical relations are calibrated at; the site's annual mean is the other defensible choice, and keeps the correction small.</source>
      <translation>校正后断面所对应的参考温度。25 °C 是岩石物理关系标定时的实验室惯例；场地年平均温度是另一个合理选择，且可使校正量较小。</translation>
    </message>
    <message>
      <source>Window the spectrum is taken over; a steady part of the record avoids switching leakage</source>
      <extracomment>Power-line frequencies offered (Hz). Noise measures of the channels shown, after each redraw.</extracomment>
      <translation>计算频谱所用的时间窗；选记录中平稳的一段，可避免通断跳变造成的频谱泄漏</translation>
    </message>
    <message>
      <source>Power-line frequency whose harmonics are marked</source>
      <translation>标出其谐波的工频</translation>
    </message>
    <message>
      <source>Reference spectrum</source>
      <translation>参考曲线频谱</translation>
    </message>
    <message>
      <source>Overlay the spectrum of the reference curve (such as the current)</source>
      <translation>叠加参考曲线（如供电电流）的频谱</translation>
    </message>
    <message>
      <source>Line frequency</source>
      <translation>工频</translation>
    </message>
    <message>
      <source>Choose a group and its channels to see their spectra.</source>
      <translation>选择一组及其通道以查看频谱。</translation>
    </message>
    <message>
      <source>Reference</source>
      <translation>参考</translation>
    </message>
    <message>
      <source>{0:g} Hz harmonic, seen at {1:g} Hz</source>
      <translation>{0:g} Hz 谐波，出现在 {1:g} Hz</translation>
    </message>
    <message>
      <source>PSD ({0})</source>
      <translation>功率谱密度（{0}）</translation>
    </message>
    <message>
      <source>Welch, Hann window · Nyquist {0:g} Hz · window: {1}</source>
      <translation>Welch 法，汉宁窗 · 奈奎斯特频率 {0:g} Hz · 时间窗：{1}</translation>
    </message>
    <message>
      <source>whole record</source>
      <translation>全段记录</translation>
    </message>
    <message>
      <source>Hayley et al. 2007 (≈2.0 %/°C)</source>
      <translation>Hayley et al. 2007 (≈2.0 %/°C)</translation>
    </message>
    <message>
      <source>Linear (Campbell/Arps)</source>
      <translation>线性 (Campbell/Arps)</translation>
    </message>
    <message>
      <source>Hayley et al. (2007) is fitted on soils and pore fluids from 0 to 25 °C. The linear form is the classic 1 + α(T − Tref) with α set below.</source>
      <translation>Hayley et al. (2007) 基于 0 至 25 °C 的土壤和孔隙流体拟合得到。线性形式为经典的 1 + α(T − Tref)，α 在下方设置。</translation>
    </message>
    <message>
      <source>Law</source>
      <translation>定律</translation>
    </message>
    <message>
      <source>Fractional resistivity change per °C in the linear law. 0.025 (2.5 %) is the standard value for pore water.</source>
      <translation>线性定律中每 °C 的电阻率相对变化量。0.025 (2.5 %) 是孔隙水的标准值。</translation>
    </message>
    <message>
      <source>α (per °C)</source>
      <translation>α（每 °C）</translation>
    </message>
    <message>
      <source>Constant temperature</source>
      <translation>恒定温度</translation>
    </message>
    <message>
      <source>Measured profile (depth × time)</source>
      <translation>实测剖面（深度 × 时间）</translation>
    </message>
    <message>
      <source>Surface record → 1-D conduction</source>
      <translation>地表记录 → 一维热传导</translation>
    </message>
    <message>
      <source>Seasonal model (depth + date)</source>
      <translation>季节模型（深度 + 日期）</translation>
    </message>
    <message>
      <source>Where the ground temperature comes from. A measured profile - a thermistor string - gives it with depth and through time, so nothing has to be modelled. Most sites only measure the surface, which is what the 1-D conduction mode is for: it diffuses that record into the ground and supplies the depth structure. One temperature per survey belongs there too - applied uniformly over depth it would correct the deep ground by what happened at the surface, which it never felt.</source>
      <translation>地温的来源。实测剖面（热敏电阻串）可直接给出随深度和时间变化的温度，无需建模。多数场地只测量地表温度，这正是一维热传导模式的用途：将该记录向地下扩散，提供随深度的结构。每期测量一个温度的情况也应使用该模式——若沿深度均匀应用，会用地表发生的变化去校正深部地层，而深部从未感受到这些变化。</translation>
    </message>
    <message>
      <source>Temperature from</source>
      <translation>温度来源</translation>
    </message>
    <message>
      <source>One temperature for the whole section and the whole sequence. This rescales every step by the same factor, so it changes the resistivity values but not the change between surveys.</source>
      <translation>整个断面和整个序列使用同一温度。这会将每一步按相同系数缩放，因此会改变电阻率值，但不改变各次勘探之间的变化。</translation>
    </message>
    <message>
      <source>Temperature</source>
      <translation>温度</translation>
    </message>
    <message>
      <source>Profile table</source>
      <translation>剖面表</translation>
    </message>
    <message>
      <source>Surface record</source>
      <translation>地表记录</translation>
    </message>
    <message>
      <source> m²/day</source>
      <translation> m²/day</translation>
    </message>
    <message>
      <source>Thermal diffusivity of the ground. Soils run about 0.04 to 0.13 m²/day; wetter and denser ground is higher. The damping depth below says what the value means in metres.</source>
      <translation>地层的热扩散率。土壤约为 0.04 至 0.13 m²/day；越湿、越致密的地层越高。下方的阻尼深度给出该值对应的米制含义。</translation>
    </message>
    <message>
      <source>Diffusivity</source>
      <translation>扩散率</translation>
    </message>
    <message>
      <source>Annual mean ground temperature, which is what the ground settles to below a few damping depths. Close to the annual mean air temperature at most sites.</source>
      <translation>年平均地温，即地下数个衰减深度以下趋于稳定的温度。在大多数场地接近年平均气温。</translation>
    </message>
    <message>
      <source>Annual mean</source>
      <translation>年均值</translation>
    </message>
    <message>
      <source>Half the peak-to-peak annual swing at the ground surface.</source>
      <translation>地表年变化峰峰值的一半。</translation>
    </message>
    <message>
      <source>Surface amplitude</source>
      <translation>地表振幅</translation>
    </message>
    <message>
      <source>Depth at which the annual swing has decayed to 1/e of its surface amplitude. Typically 2–3 m in soils, more in dry coarse ground. Below about three of these the correction stops varying with the season.</source>
      <translation>年变幅衰减至地表振幅 1/e 时的深度。土壤中通常为 2–3 m，干燥粗粒地层中更大。在约三倍该深度以下，校正量不再随季节变化。</translation>
    </message>
    <message>
      <source>Damping depth</source>
      <translation>衰减深度</translation>
    </message>
    <message>
      <source>Day of the year the ground surface is warmest: about 200 (mid-July) in the northern hemisphere, about 20 in the southern.</source>
      <translation>地表温度最高的年内日序：北半球约为 200（7 月中旬），南半球约为 20。</translation>
    </message>
    <message>
      <source>Warmest day</source>
      <translation>最热日</translation>
    </message>
    <message>
      <source>Correct the section on screen with these settings. Press again after changing them; nothing is corrected until you do.</source>
      <translation>使用这些设置校正屏幕上的断面。更改设置后需再次按下；在此之前不会进行任何校正。</translation>
    </message>
    <message>
      <source>Show the resistivity as inverted again.</source>
      <translation>重新显示反演所得电阻率。</translation>
    </message>
    <message>
      <source>Temperature record</source>
      <translation>温度记录</translation>
    </message>
    <message>
      <source>Annual swing falls to 1/e by about {0:.1f} m, and is negligible below roughly {1:.0f} m.</source>
      <translation>年变幅在约 {0:.1f} m 处衰减至 1/e，在约 {1:.0f} m 以下可忽略。</translation>
    </message>
    <message>
      <source>Bodies known or assumed in the ground - a clay layer, a tank, a plume - as boxes. The mesh can follow their faces, each can be a region of its own, and the 3D forward model gives each its resistivity.</source>
      <extracomment>How far a layer reaches past the survey sideways: beyond any domain the builder makes, so that it spans whatever mesh it is used on. Where a new zone goes before the page has said where the survey is: the default surface grid, down to the default investigation depth.</extracomment>
      <translation>地下已知或假定的地质体——如黏土层、储罐、污染羽——以长方体表示。网格可贴合其表面，每个地质体可作为独立区域，3D 正演会为每个地质体赋予其电阻率。</translation>
    </message>
    <message>
      <source>Double-click a name to rename the zone. Cells counts the inverted cells the zone took in the last mesh built; where zones overlap, the one lower in the list takes the cell.</source>
      <translation>双击名称可重命名分区。“单元”统计该分区在最近一次构建的网格中所占的反演单元数；分区重叠时，单元归列表中靠下的分区。</translation>
    </message>
    <message>
      <source>Add zone</source>
      <translation>添加分区</translation>
    </message>
    <message>
      <source>A box under the middle of the survey, in the upper half of the inverted region; set its extent below.</source>
      <translation>位于测区中部下方、反演区域上半部的长方体；在下方设置其范围。</translation>
    </message>
    <message>
      <source>Add layer</source>
      <translation>添加层</translation>
    </message>
    <message>
      <source>A zone spanning the whole mesh sideways, from the ground (or the bottom of the layer added before it) down a third of the inverted region. It goes in the list after the layers and before the other zones, so that a zone inside it keeps its cells.</source>
      <translation>横向贯穿整个网格的分区，自地面（或前一添加层的底部）向下延伸至反演区域的三分之一。它在列表中位于各层之后、其他分区之前，从而使其内部的分区保留自己的单元。</translation>
    </message>
    <message>
      <source>Remove the selected zone.</source>
      <translation>移除所选分区。</translation>
    </message>
    <message>
      <source>to</source>
      <translation>至</translation>
    </message>
    <message>
      <source>Build the mesh so that every zone face is made of cell faces, the way E4D meshes its zones: no cell straddles a face, so a zone's resistivity covers exactly the box. E4D meshes each zone as a zone of its own, the structured grid puts a grid line on every face, the prism mesh adds the outlines to its plan triangulation and a layer at every top and bottom, and Gmsh cuts the boxes into its domain. Generate the mesh again after moving a zone. Without it a zone takes the cells whose centre lies inside it.</source>
      <translation>构建网格时使每个分区面均由单元面组成，与 E4D 对分区的剖分方式相同：没有单元跨越分区面，因此分区的电阻率恰好覆盖该长方体。E4D 将每个分区单独剖分；结构化网格在每个面上设置网格线；棱柱网格将轮廓加入平面三角剖分，并在每个顶面和底面处加一层；Gmsh 将长方体切入其计算域。移动分区后需重新生成网格。不启用时，分区取中心位于其内部的单元。</translation>
    </message>
    <message>
      <source>Make each zone a region of its own - markers {0}, {1}, ... in the order of the list - so that an inversion of this mesh in PyGIMLi may put a sharp contrast at its faces: PyGIMLi puts no smoothness constraint between regions. Only inverted cells are zoned; the outer region keeps its marker. Off, the zones stay in the inverted region (marker 2) and are smoothed across like the rest.</source>
      <translation>将每个分区设为独立区域（按列表顺序使用标记 {0}、{1}、...），使 PyGIMLi 对该网格反演时可在分区界面处形成明显的突变：PyGIMLi 在区域之间不施加光滑约束。只有反演单元会被分区；外部区域保留其标记。关闭时，各分区保留在反演区域（标记 2）中，并与其余部分一样跨界光滑。</translation>
    </message>
    <message>
      <source>Across the whole mesh, z {0:g} to {1:g} m</source>
      <translation>贯穿整个网格，z {0:g} 至 {1:g} m</translation>
    </message>
    <message>
      <source>x {0:g} to {1:g}, y {2:g} to {3:g}, z {4:g} to {5:g} m</source>
      <translation>x {0:g} 至 {1:g}，y {2:g} 至 {3:g}，z {4:g} 至 {5:g} m</translation>
    </message>
    <message>
      <source>This zone took no cell in the last mesh: it lies outside the inverted region, or zones lower in the list cover it.</source>
      <translation>在上次网格中此分区未包含任何单元：它位于反演区域之外，或被列表中靠下的分区覆盖。</translation>
    </message>
    <message>
      <source>Box select</source>
      <translation>框选</translation>
    </message>
    <message>
      <source>Drag a box on the pseudosection to select readings, then Reject or Restore them.</source>
      <translation>在拟断面上拖出矩形框选读数，然后剔除或恢复。</translation>
    </message>
    <message>
      <source>Saved as dataset {0}, version {1}</source>
      <translation>已保存为数据集 {0}，版本 {1}</translation>
    </message>
    <message>
      <source>Select periods</source>
      <translation>选择周期</translation>
    </message>
    <message>
      <source>Drag across the curves to select periods, then Reject or Restore them.</source>
      <translation>在曲线上横向拖动选择周期，然后剔除或恢复。</translation>
    </message>
    <message>
      <source>Reason (kept in the record)</source>
      <extracomment>Labels of the record's Action column, here so the translation catalog has them.</extracomment>
      <translation>原因（记入记录）</translation>
    </message>
    <message>
      <source>Reject selected</source>
      <translation>剔除所选</translation>
    </message>
    <message>
      <source>Restore selected</source>
      <translation>恢复所选</translation>
    </message>
    <message>
      <source>Record…</source>
      <translation>记录…</translation>
    </message>
    <message>
      <source>Leave the selected items out of processing and inversion; the decision is recorded.</source>
      <translation>所选项不参与处理与反演；该决定会被记录。</translation>
    </message>
    <message>
      <source>Use the selected items again; recorded too.</source>
      <translation>重新使用所选项；同样会被记录。</translation>
    </message>
    <message>
      <source>Every decision with its reason and time; export it, or save it with the data.</source>
      <translation>列出每项决定及其原因和时间；可导出，或与数据一起保存。</translation>
    </message>
    <message>
      <source>{0} of {1} rejected</source>
      <translation>已剔除 {0}/{1}</translation>
    </message>
    <message>
      <source>Select items first (drag a box, or pick rows).</source>
      <translation>请先选择（拖框或选中表格行）。</translation>
    </message>
    <message>
      <source>QC record</source>
      <translation>质控记录</translation>
    </message>
    <message>
      <source>Export CSV…</source>
      <translation>导出 CSV…</translation>
    </message>
    <message>
      <source>Save with the data</source>
      <translation>与数据一起保存</translation>
    </message>
    <message>
      <source>Export QC record</source>
      <translation>导出质控记录</translation>
    </message>
    <message>
      <source>Standard</source>
      <extracomment>Code -&gt; (Chinese title, English title), as published. Page key -&gt; control attribute -&gt; (standards, subject in Chinese, subject in English).</extracomment>
      <translation>规程</translation>
    </message>
    <message>
      <source>3D options</source>
      <extracomment>What a renderer raises when its window or a draw fails (VTK reports GL failures as RuntimeError). Camera preset names (English source text, translated when shown). Layer switches: option field -&gt; (label, default) (English source text).</extracomment>
      <translation>三维选项</translation>
    </message>
    <message>
      <source>Vertical exaggeration of elevations and depths</source>
      <translation>高程与深度的纵向夸大倍数</translation>
    </message>
    <message>
      <source>All</source>
      <translation>全部</translation>
    </message>
    <message>
      <source>Show pseudo-depth points down to this depth (All: every point)</source>
      <translation>只显示拟深度不超过此值的点（全部：显示所有点）</translation>
    </message>
    <message>
      <source>Exaggeration</source>
      <translation>纵向夸大</translation>
    </message>
    <message>
      <source>Point size</source>
      <translation>点大小</translation>
    </message>
    <message>
      <source>Max pseudo-depth</source>
      <translation>最大拟深度</translation>
    </message>
    <message>
      <source>View</source>
      <translation>视角</translation>
    </message>
    <message>
      <source>Parallel projection</source>
      <translation>平行投影</translation>
    </message>
    <message>
      <source>Tools</source>
      <translation>工具</translation>
    </message>
    <message>
      <source>Measure distance</source>
      <translation>测距</translation>
    </message>
    <message>
      <source>Screenshot…</source>
      <translation>截图…</translation>
    </message>
    <message>
      <source>Export VTK…</source>
      <translation>导出 VTK…</translation>
    </message>
    <message>
      <source>Use simple 3D (no graphics card)</source>
      <translation>使用简易三维（不需要显卡）</translation>
    </message>
    <message>
      <source>Draw with Matplotlib, not PyVista: slower, but works without a graphics driver</source>
      <translation>用 Matplotlib 代替 PyVista 绘制：较慢，但没有显卡驱动也能用</translation>
    </message>
    <message>
      <source>Needs the PyVista 3D view</source>
      <translation>需要 PyVista 三维视图</translation>
    </message>
    <message>
      <source>Drag to rotate, scroll to zoom; right-click a point to select it.</source>
      <translation>拖动旋转，滚轮缩放；右键单击点可选中。</translation>
    </message>
    <message>
      <source>Drag to rotate; click a point to select it.</source>
      <translation>拖动旋转；单击点可选中。</translation>
    </message>
    <message>
      <source>Simple 3D view: {0}</source>
      <translation>简易三维视图：{0}</translation>
    </message>
    <message>
      <source>East ({0})</source>
      <translation>东（{0}）</translation>
    </message>
    <message>
      <source>North ({0})</source>
      <translation>北（{0}）</translation>
    </message>
    <message>
      <source>Elevation ({0})</source>
      <translation>高程（{0}）</translation>
    </message>
    <message>
      <source>The 3D view could not draw: {0}</source>
      <translation>三维视图无法绘制：{0}</translation>
    </message>
    <message>
      <source>{0}: {1:.2f} km from the line centre</source>
      <translation>{0}：距测线中心 {1:.2f} km</translation>
    </message>
    <message>
      <source>Save screenshot</source>
      <translation>保存截图</translation>
    </message>
    <message>
      <source>Export VTK</source>
      <translation>导出 VTK</translation>
    </message>
    <message>
      <source>Distance: {0:.2f} m</source>
      <translation>距离：{0:.2f} m</translation>
    </message>
    <message>
      <source>2D</source>
      <extracomment>Tab keys, in order. The tab on screen or the 2-D/3-D choice changed (a page refreshes its toolbar on it).</extracomment>
      <translation>二维</translation>
    </message>
    <message>
      <source>Plan and section</source>
      <translation>平面图与剖面图</translation>
    </message>
    <message>
      <source>3D</source>
      <translation>三维</translation>
    </message>
    <message>
      <source>Three-dimensional view</source>
      <translation>三维视图</translation>
    </message>
    <message>
      <source>Layout</source>
      <translation>布设图</translation>
    </message>
    <message>
      <source>Curves</source>
      <translation>曲线</translation>
    </message>
    <message>
      <source>Spectrum</source>
      <translation>频谱</translation>
    </message>
    <message>
      <source>Plan figure…</source>
      <translation>平面图…</translation>
    </message>
    <message>
      <source>Section figure…</source>
      <translation>剖面图…</translation>
    </message>
    <message>
      <source>Curve figure…</source>
      <translation>曲线图…</translation>
    </message>
    <message>
      <source>Spectrum figure…</source>
      <translation>频谱图…</translation>
    </message>
    <message>
      <source>Save figure</source>
      <translation>保存图件</translation>
    </message>
    <message>
      <source>PDF (*.pdf);;PNG (*.png);;SVG (*.svg)</source>
      <translation>PDF (*.pdf);;PNG (*.png);;SVG (*.svg)</translation>
    </message>
    <message>
      <source>Colour the pseudo-depth points by one of their values</source>
      <extracomment>Legends of the pseudo-depth conventions (English source text; see survey.pseudo.CONVENTIONS). Attributes usually drawn on a log scale.</extracomment>
      <translation>按拟深度点的某项数值着色</translation>
    </message>
    <message>
      <source>Log scale</source>
      <translation>对数刻度</translation>
    </message>
    <message>
      <source>Terrain</source>
      <translation>地形</translation>
    </message>
    <message>
      <source>Drag a box to select the readings inside it</source>
      <translation>拖出方框，选中框内的测量</translation>
    </message>
    <message>
      <source>Distance along the line</source>
      <translation>沿测线距离</translation>
    </message>
    <message>
      <source>Elevation</source>
      <translation>高程</translation>
    </message>
    <message>
      <source>Show or hide the view options</source>
      <translation>显示或隐藏视图选项</translation>
    </message>
    <message>
      <source>Colour the points by one of their values</source>
      <extracomment>Role names as a legend shows them (English source text, translated when shown). The user picked a point: its key (a tuple) and its group.</extracomment>
      <translation>按点的某项数值着色</translation>
    </message>
    <message>
      <source>Include remote B</source>
      <translation>包含远端 B</translation>
    </message>
    <message>
      <source>Show a remote electrode where it is (rescales the plan); otherwise an arrow points to it.</source>
      <translation>按实际位置画出远端电极（平面图会随之缩放）；否则用箭头指向它。</translation>
    </message>
    <message>
      <source>Other shots</source>
      <translation>其他炮</translation>
    </message>
    <message>
      <source>Show the sources of the other groups, faded</source>
      <translation>淡色显示其他组的供电点</translation>
    </message>
    <message>
      <source>Drag a box to select the points inside it</source>
      <translation>拖出方框，选中框内的点</translation>
    </message>
    <message>
      <source>Colour by</source>
      <translation>着色依据</translation>
    </message>
    <message>
      <source>Role</source>
      <translation>类型</translation>
    </message>
    <message>
      <source>East</source>
      <translation>东</translation>
    </message>
    <message>
      <source>North</source>
      <translation>北</translation>
    </message>
    <message>
      <source>No survey layout to show.</source>
      <translation>没有可显示的布设。</translation>
    </message>
    <message>
      <source>CRS: {0}</source>
      <translation>坐标系：{0}</translation>
    </message>
    <message>
      <source>{0} {1}: {2:.2f} km away ({3:.0f}, {4:.0f})</source>
      <translation>{0} {1}：距离 {2:.2f} km（{3:.0f}, {4:.0f}）</translation>
    </message>
    <message>
      <source>Zoom the time axis to a window of the record</source>
      <extracomment>Window names the adapters use (English source text, translated when shown). Shading of each window kind.</extracomment>
      <translation>把时间轴缩放到记录的某个时间窗</translation>
    </message>
    <message>
      <source>Shade windows</source>
      <translation>标出时间窗</translation>
    </message>
    <message>
      <source>Reference curve</source>
      <translation>参考曲线</translation>
    </message>
    <message>
      <source>Draw the reference curve (such as the current) on the right axis</source>
      <translation>在右纵轴上画参考曲线（如供电电流）</translation>
    </message>
    <message>
      <source>Choose a group and its channels to see their curves.</source>
      <translation>选择一组及其通道以查看曲线。</translation>
    </message>
    <message>
      <source>{0} channels · {1} samples · {2:g} samples/s</source>
      <translation>{0} 个通道 · {1} 个样点 · 每秒 {2:g} 个样点</translation>
    </message>
    <message>
      <source>Field units (mV/km, nT)</source>
      <translation>场值单位（mV/km、nT）</translation>
    </message>
    <message>
      <source>Remove the instrument response before drawing the curves</source>
      <translation>绘制曲线前先去除仪器响应</translation>
    </message>
    <message>
      <source>{0:g} Hz · {1:.1f} min</source>
      <translation>{0:g} Hz · {1:.1f} 分钟</translation>
    </message>
    <message>
      <source>Workflow</source>
      <translation>工作流</translation>
    </message>
    <message>
      <source>Seismic Processing</source>
      <translation>地震处理</translation>
    </message>
    <message>
      <source>ERT Processing</source>
      <translation>ERT 处理</translation>
    </message>
    <message>
      <source>3D Mesh Builder</source>
      <translation>3D 网格构建器</translation>
    </message>
    <message>
      <source>EM Processing</source>
      <translation>EM 处理</translation>
    </message>
    <message>
      <source>Magnetotellurics</source>
      <translation>大地电磁</translation>
    </message>
    <message>
      <source>Ground-Penetrating Radar</source>
      <translation>探地雷达</translation>
    </message>
    <message>
      <source>Boreholes</source>
      <translation>钻孔</translation>
    </message>
    <message>
      <source>Joint Inversion</source>
      <translation>联合反演</translation>
    </message>
    <message>
      <source>Data &amp; reports</source>
      <translation>数据与报告</translation>
    </message>
    <message>
      <source>EM</source>
      <translation>EM</translation>
    </message>
    <message>
      <source>ERT</source>
      <translation>ERT</translation>
    </message>
    <message>
      <source>GPR</source>
      <translation>GPR</translation>
    </message>
    <message>
      <source>Seismic</source>
      <translation>地震</translation>
    </message>
    <message>
      <source>Project</source>
      <translation>工程</translation>
    </message>
    <message>
      <source>Saved Results</source>
      <translation>已保存结果</translation>
    </message>
    <message>
      <source>[binary file; use filename, format and task evidence]</source>
      <translation>[二进制文件；请依据文件名、格式和任务信息判断]</translation>
    </message>
    <message>
      <source>You are {name} ({title}), an assistant embedded in the PyHydroGeophysX desktop studio. {summary} You help the user by driving the studio GUI through tools. Where the studio cannot do what is needed, you can propose a short temporary script, which runs only if the user approves it.

Rules:
- You act only through the provided tools: list_modules, navigate, describe_current_module, apply_action, get_studio_state, run_to_report, propose_script.
- When something fails or the studio has no action for what is needed, think about the cause before giving up or handing the problem back. First look for a way with the studio's own actions (another action, other parameters, another module). If there is none, and a few lines of Python would get past it - a file in a layout a module cannot read, one module's result in a format another module has no action to take, a number no module computes - call propose_script. Check the module's actions first: the water-content module, for example, takes the ERT page's model with use_ert_model and opens an inversion's output folder with set_data_dir, so it needs no script for that. A script must never invent layer markers: an inversion mesh's cell markers number cells, they are not layers. In its purpose, say plainly what went wrong, what the script will do and what you will do with its output. The user sees the code and decides; if they reject it, accept that and offer the other options. After it runs, use what it wrote through the studio's actions (for example set_data_dir on the folder it wrote). If it fails, read its error and what it printed, fix the cause (not with a bare except or a made-up value) and call propose_script again with the corrected script and a purpose that says what was wrong; the user approves it again. If a fix does not help either, say so and offer another way rather than a third version. Never propose the same script unchanged. Never present a script's guess as a measured result.
- The user chose to work step by step, and can change their mind at any point. When they ask for the end result rather than the next step - in any words or language, e.g. "give me the final result directly", "just finish it", "use auto report", "直接给我结果" - call run_to_report in that same turn, with ask_user false since they asked for it. It hands the rest of the task to Auto to report, which carries on from where you are now, reuses what is already done, and writes the report. Never tell the user to switch modes themselves; switching is what run_to_report does. In its goal, restate the whole task as the run should read it: what the user asked for, the data and every choice made so far (instrument, geometry, single or time-lapse, inversion settings and the fit obtained), and what is left to do.
- Pick the module by matching the task to the module purposes listed under "Studio modules" below — read them before choosing.
- You decide which calls the user approves, with each call's ask_user argument. Calls with ask_user false run at once and the user sees them in the chat; calls with ask_user true wait for Approve / Reject. Ask where the user's judgement matters: before a long computation (an inversion, a forward run, picking every shot) whose settings they have not confirmed, when you choose a value, data source or method they did not give, and before a change of plan. Do not ask for routine work: looking, opening a module, loading the data they named, applying values they gave, the next step of a plan they already agreed to. A task of ten steps should ask once or twice, at its decisions. Clearing or removing picks, electrodes or inputs, exporting or saving to a path you name, and running a script, always wait for the user whatever you set.
- Never ask for permission in words ("Shall I proceed?"): briefly say what you are about to do and make the tool call in the same turn, with ask_user true if it needs their say.
- Think the whole task through before the first action: what the goal needs, which modules and actions get there, what could go wrong. Say the plan in a sentence or two, then revise it as results come in.
- Take one action at a time: call a single tool, wait for its result, then decide the next step.
- The usual order of a module's actions is a default, not a rule. When the results show a better path - running a step again with other parameters, a check in another module, a product the goal implies that nobody asked for - say what you would do differently, why, and what it should gain, and make that call with ask_user true; the user decides through the approval card. If they reject it, carry on along the usual path.
- navigate returns the opened module's description under "current_module": its actions with their parameter keys, its current state and its views. Use those real action names and parameter keys in apply_action. Do not call describe_current_module right after navigate - it would return the same description again; call it only to refresh the state later (for example after data were loaded or a run finished), or when no navigate result is at hand.
- Never invent file paths or other inputs. If an action needs a data file and the user did not give you a path, prefer an example-data action (such as use_example_data or use_example) when the module offers one, unless a rule below says to ask first; only call load_data with a path the user actually provided. If neither is possible, ask the user for the file.
- For a processing request, a typical sequence is: navigate to the right module (its result describes the module), load data (use the example data if the user gave none), set parameters, then run.
- If a tool result has status "failed" or "declined", read it and adjust, or ask the user what to do. Do not invent module names, actions, or parameters; discover them with the tools.
- A message that starts with "[Studio]" comes from the studio, not the user: it reports something that happened, such as an automatic run that failed. Do what it asks, and address the user in your reply.
- Always finish your turn by telling the user the next step: what you will do next, or what they can ask for. When you START a long job (a tool result with status "started"), say it is running in the background and that the user can ask for its status (for example "is it done?") or say "continue" to proceed once it finishes — then end your turn rather than guessing the job is complete.
- After a background job, refresh the module's status before reporting progress. Read inversion_status, inversion_running, has_model and result_summary when provided. A completed model is available for review in the processing module even before saving it or adding it to Map. Report the returned fit metrics; if a metric is missing, say it is unavailable rather than claiming no model exists. If a new run is running or failed while an earlier model remains, distinguish the latest run from that earlier result.
- When a tool returns status "awaiting_user", the workflow is paused for the user to act in the GUI (for example correcting picks). Relay the message, end your turn, and resume only when the user says to continue.
{persona}{vision_rules}{skill_rules}
Studio modules (key: purpose):
{modules}
</source>
      <translation>你是 {name}（{title}），一个嵌入在 PyHydroGeophysX 桌面 Studio 中的助手。{summary} 你通过工具操作 Studio 的图形界面来帮助用户。当 Studio 无法完成所需操作时，你可以提议一个简短的临时脚本，该脚本仅在用户批准后运行。

规则：
- 你只能通过所提供的工具行事：list_modules、navigate、describe_current_module、apply_action、get_studio_state、run_to_report、propose_script。
- 当某个操作失败，或 Studio 没有满足需求的动作时，先思考原因，再决定是否放弃或把问题交还给用户。首先寻找使用 Studio 自身动作的途径（另一个动作、其他参数、另一个模块）。如果没有，而几行 Python 就能解决——某个模块无法读取的文件布局、某模块的结果格式另一个模块没有动作可以接收、没有任何模块计算的某个数值——就调用 propose_script。先检查模块的动作：例如，含水量模块可通过 use_ert_model 接收 ERT 页面的模型，并通过 set_data_dir 打开反演的输出文件夹，因此这种情况不需要脚本。脚本绝不能凭空编造层标记：反演网格的单元标记是单元编号，而不是层。在 purpose 中清楚说明出了什么问题、脚本将做什么以及你将如何使用其输出。用户会看到代码并作出决定；如果用户拒绝，请接受并提供其他选项。脚本运行后，通过 Studio 的动作使用它写出的内容（例如对它写出的文件夹执行 set_data_dir）。如果脚本失败，阅读其错误和输出，修复根本原因（不要用裸 except 或编造的数值），并用修正后的脚本和说明问题所在的 purpose 再次调用 propose_script；用户会再次审批。如果修复仍然无效，请如实说明并提供其他途径，而不是写第三个版本。绝不要原样重复提议同一个脚本。绝不要把脚本的猜测当作实测结果呈现。
- 用户选择了逐步操作，并可随时改变主意。当用户要求直接得到最终结果而不是下一步时——无论用什么措辞或语言，例如 "give me the final result directly"、"just finish it"、"use auto report"、"直接给我结果"——请在同一轮中调用 run_to_report，并将 ask_user 设为 false，因为这是用户主动要求的。它会把剩余任务交给“自动出报告”模式，从当前进度继续，复用已完成的工作并撰写报告。绝不要让用户自己切换模式；run_to_report 本身就负责切换。在其 goal 中，按运行所需的方式完整重述整个任务：用户的要求、数据以及迄今作出的每个选择（仪器、几何、单次或时移、反演设置及获得的拟合结果），以及剩余待完成的工作。
- 将任务与下方 "Studio 模块" 中列出的模块用途进行匹配来选择模块——选择前请先阅读这些用途。
- 由你通过每次调用的 ask_user 参数决定哪些调用需要用户批准。ask_user 为 false 的调用会立即运行，用户会在聊天中看到；ask_user 为 true 的调用会等待“批准/拒绝”。在用户的判断起作用的地方询问：在设置尚未经用户确认的长时间计算（反演、正演、拾取所有炮）之前，在你选择了用户未给定的数值、数据源或方法时，以及在改变计划之前。不要为常规工作询问：查看、打开模块、载入用户指定的数据、应用用户给定的数值、执行用户已同意的计划中的下一步。一个十步的任务应只在其决策点询问一两次。清除或删除拾取、电极或输入，导出或保存到你指定的路径，以及运行脚本，无论你如何设置，始终会等待用户确认。
- 绝不要用文字征求许可（"Shall I proceed?"）：简要说明你将要做什么，并在同一轮中发起工具调用；如需用户决定，则将 ask_user 设为 true。
- 在第一个动作之前通盘考虑整个任务：目标需要什么、哪些模块和动作可以达成、可能出现什么问题。用一两句话说明计划，然后随结果的出现不断修订。
- 一次只执行一个动作：调用单个工具，等待其结果，再决定下一步。
- 模块动作的常规顺序只是默认做法，而非规则。当结果表明有更好的路径时——用其他参数重新运行某一步、在另一个模块中做检查、目标隐含但无人要求的某个成果——说明你会有何不同做法、原因以及预期收益，并以 ask_user true 发起该调用；用户通过审批卡片决定。如果用户拒绝，则沿常规路径继续。
- navigate 会在 "current_module" 下返回所打开模块的描述：其动作及参数键、当前状态和视图。在 apply_action 中使用这些真实的动作名称和参数键。不要在 navigate 之后立即调用 describe_current_module——它会再次返回相同的描述；只在之后需要刷新状态时（例如数据载入后或运行结束后），或手头没有 navigate 结果时才调用它。
- 绝不要编造文件路径或其他输入。如果某个动作需要数据文件而用户没有提供路径，且模块提供示例数据动作（如 use_example_data 或 use_example），则优先使用它，除非下方某条规则要求先询问；只有在用户确实提供了路径时才调用 load_data。如果两者都不可行，请向用户索要文件。
- 对于处理请求，典型顺序是：导航到正确的模块（其结果会描述该模块），载入数据（若用户未提供则使用示例数据），设置参数，然后运行。
- 如果工具结果的 status 为 "failed" 或 "declined"，请阅读并调整，或询问用户如何处理。不要编造模块名称、动作或参数；通过工具去发现它们。
- 以 "[Studio]" 开头的消息来自 Studio 而非用户：它报告已发生的事情，例如某次自动运行失败。按其要求去做，并在回复中面向用户。
- 每一轮结束时都要告诉用户下一步：你接下来要做什么，或用户可以提出什么请求。当你启动一个长时间作业（工具结果的 status 为 "started"）时，说明它正在后台运行，用户可以询问其状态（例如 "is it done?"），或在完成后发送 "continue" 继续——然后结束本轮，不要猜测作业已经完成。
- 后台作业结束后，先刷新模块状态再报告进度。如有提供，读取 inversion_status、inversion_running、has_model 和 result_summary。已完成的模型即使尚未保存或添加到地图，也可在处理模块中查看。报告返回的拟合指标；若某项指标缺失，请说明其不可用，而不要声称没有模型。如果新的运行正在进行或已失败，而先前的模型仍在，请区分最新运行与先前结果。
- 当工具返回 status "awaiting_user" 时，工作流已暂停，等待用户在界面中操作（例如修正拾取）。转达该消息，结束本轮，仅在用户表示继续时再恢复。
{persona}{vision_rules}{skill_rules}
Studio 模块（键：用途）：
{modules}
</translation>
    </message>
    <message>
      <source>- Written procedures (skills) are listed below by name and when they apply. Before a task one of them covers, read it with read_skill (it runs at once and changes nothing), then follow it where it fits the data and the request. A procedure is its author's advice: it never overrides the user, the checkpoints above or what the data show, and it is not a reason to skip asking. Say which procedure you followed.
Written procedures:
{index}
</source>
      <translation>- 下面按名称列出了书面流程（技能）及其适用情形。在执行某个流程所涵盖的任务之前，先用 read_skill 读取它（立即运行，不做任何更改），然后在适合数据和请求的范围内遵循它。流程只是其作者的建议：它绝不凌驾于用户、上述检查点或数据所显示的内容之上，也不能作为跳过询问的理由。请说明你遵循了哪个流程。
书面流程：
{index}
</translation>
    </message>
    <message>
      <source>- You can see the studio. capture_view takes a picture of a panel in the current module and shows it to you; the module's description (from navigate or describe_current_module) lists the panel names under "views". Use it to judge what numbers do not show: artefacts or implausible structure in an inversion section, picks that follow noise instead of the first arrival, a mesh with the wrong extent or bad element shape. Say which view you looked at, report what is actually in the picture, and say plainly when the image is too coarse to judge rather than guessing.
- Do not capture after every step. One picture costs about as much context as a long message, so capture when a result is worth judging visually, never to confirm that a parameter was set.
- When a capture_view result carries a "context" field, those numbers are exact and the picture is not. Never read an index, a trace number or a coordinate off the image when "context" gives it to you: dozens of items can share one axis and the marker sits far from its tick label, so counting across a plot is where you will be wrong. Judge quality from the picture, then name the item from the numbers. If the two disagree, trust the numbers for identity and say what the picture showed you.
- If the user asks about pick quality while a first-break review is paused, capture_view the 'gather' view before answering, and cross-check its "context" pick table against what you see.
</source>
      <translation>- 你可以看到 Studio。capture_view 会截取当前模块中某个面板的图像并展示给你；模块的描述（来自 navigate 或 describe_current_module）在 "views" 下列出了面板名称。用它来判断数字无法体现的内容：反演断面中的伪影或不合理结构、跟随噪声而非初至的拾取、范围错误或单元形状不佳的网格。说明你查看了哪个视图，报告图像中实际呈现的内容；当图像过于粗糙无法判断时，请直接说明，不要猜测。
- 不要每一步之后都截图。一张图片占用的上下文约相当于一条长消息，因此只在结果值得直观评判时截图，绝不要用来确认某个参数已设置。
- 当 capture_view 结果带有 "context" 字段时，其中的数字是精确的，而图像不是。只要 "context" 已给出，就绝不要从图像上读取索引、道号或坐标：几十个项目可能共用一条坐标轴，标记离其刻度标签很远，跨图计数正是最容易出错的地方。根据图像判断质量，再根据数字确定是哪一项。若两者不一致，以数字确定身份，并说明图像显示了什么。
- 如果用户在初至审核暂停时询问拾取质量，请在回答前对 'gather' 视图执行 capture_view，并将其 "context" 中的拾取表与所见内容交叉核对。
</translation>
    </message>
    <message>
      <source>[Studio] The job you started on the {title} page ({module}) failed after your turn ended. What the page logged:
{errors}

Find out why before you answer: describe_current_module (navigate to {module} first if the user has moved on) shows the page's state and its actions. Then tell the user in a few sentences what went wrong, and fix what you can: other settings, other input, another action or module, or a temporary script where the studio has no way. Ask the user (ask_user true) before running the job again or making a choice that is theirs. If nothing you can do would help, say plainly what is missing.</source>
      <translation>[Studio] 你在 {title} 页面（{module}）上启动的作业在你的回合结束后失败了。该页面记录的内容：
{errors}

回答之前先查明原因：describe_current_module（如果用户已切换到别处，先导航到 {module}）会显示页面状态及其动作。然后用几句话告诉用户出了什么问题，并修复你能修复的部分：其他设置、其他输入、另一个动作或模块，或在 Studio 无法处理时提议临时脚本。在重新运行作业或作出应由用户决定的选择之前，先询问用户（ask_user true）。如果你无能为力，请直接说明缺少什么。</translation>
    </message>
    <message>
      <source>[Studio] The {title} page ({module}) reported an error that none of your tool calls returned - most likely something the user did on the page, or work they started there. What the page reported:
{errors}

Look before you answer: navigate to {module} if it is not the current module, and read its state with describe_current_module. Then tell the user in a few sentences what went wrong and how to put it right. If it is something they can simply correct (a wrong file, a missing input, a setting out of range), say what to do. Offer to do it for them, and ask (ask_user true) before you change their settings or run anything: this was their operation.</source>
      <translation>[Studio] {title} 页面（{module}）报告了一个错误，但你的任何工具调用都没有返回它——很可能是用户在该页面上的操作，或用户在那里启动的工作所致。该页面报告的内容：
{errors}

回答之前先查看：如果 {module} 不是当前模块，先导航到它，并用 describe_current_module 读取其状态。然后用几句话告诉用户出了什么问题以及如何纠正。如果是用户可以简单更正的问题（文件错误、缺少输入、设置超出范围），说明该怎么做。主动提出代为处理，并在更改用户设置或运行任何内容之前先询问（ask_user true）：这是用户自己的操作。</translation>
    </message>
    <message>
      <source>[Studio] The automatic run {how}. What it reported:
{report}

Find out why before you answer: apply_action get_status on the Workflow page (module one_click) gives the run's steps with their status, its warnings and its output folder, and the module a failed step ran in shows its state. Then tell the user in a few sentences what went wrong, and fix what you can: correct an input or a setting with the studio's actions and run the task again with run_to_report, finish the missing part step by step, or propose a temporary script where the studio has no way. Ask the user (ask_user true) before running the task again or making a choice that is theirs. If nothing you can do would help, say plainly what is missing and what the user could provide.</source>
      <translation>[Studio] 自动运行{how}。其报告内容：
{report}

回答之前先查明原因：在工作流页面（模块 one_click）上执行 apply_action get_status，可获得该运行的各步骤及其状态、警告和输出文件夹；失败步骤所在的模块会显示其状态。然后用几句话告诉用户出了什么问题，并修复你能修复的部分：用 Studio 的动作更正输入或设置并用 run_to_report 重新运行任务，逐步完成缺失的部分，或在 Studio 无法处理时提议临时脚本。在重新运行任务或作出应由用户决定的选择之前，先询问用户（ask_user true）。如果你无能为力，请直接说明缺少什么以及用户可以提供什么。</translation>
    </message>
    <message>
      <source>Select a model or enter a model ID.</source>
      <translation>选择一个模型或输入模型 ID。</translation>
    </message>
    <message>
      <source>Workflow page could not be loaded. See the Studio log.</source>
      <translation>无法加载工作流页面。请查看 Studio 日志。</translation>
    </message>
    <message>
      <source>Reference documents (RAG)</source>
      <translation>参考文档 (RAG)</translation>
    </message>
    <message>
      <source>PyHydroGeophysX Professional Studio</source>
      <translation>PyHydroGeophysX Professional Studio</translation>
    </message>
    <message>
      <source>Forward</source>
      <translation>正演</translation>
    </message>
    <message>
      <source>Simulate a survey</source>
      <translation>模拟测量</translation>
    </message>
    <message>
      <source>Hydrologic model → petrophysics → predicted response.</source>
      <translation>水文模型 → 岩石物理 → 预测响应。</translation>
    </message>
    <message>
      <source>Inverse</source>
      <translation>反向</translation>
    </message>
    <message>
      <source>Invert field data</source>
      <translation>反演野外数据</translation>
    </message>
    <message>
      <source>Load, invert and evaluate measured data.</source>
      <translation>载入、反演并评估实测数据。</translation>
    </message>
    <message>
      <source>Estimate hydrology</source>
      <translation>估算水文参数</translation>
    </message>
    <message>
      <source>Structure, water content and porosity, with uncertainty.</source>
      <translation>结构、含水量和孔隙度，附不确定度。</translation>
    </message>
    <message>
      <source>Log</source>
      <translation>日志</translation>
    </message>
    <message>
      <source>Metres (m)</source>
      <translation>米 (m)</translation>
    </message>
    <message>
      <source>Feet (ft)</source>
      <translation>英尺 (ft)</translation>
    </message>
    <message>
      <source>Match System</source>
      <translation>跟随系统</translation>
    </message>
    <message>
      <source>Light</source>
      <translation>浅色</translation>
    </message>
    <message>
      <source>Dark</source>
      <translation>深色</translation>
    </message>
    <message>
      <source>The assistant</source>
      <translation>助手</translation>
    </message>
    <message>
      <source>Finished</source>
      <translation>已完成</translation>
    </message>
    <message>
      <source>Error</source>
      <translation>错误</translation>
    </message>
    <message>
      <source>Warnings</source>
      <translation>警告</translation>
    </message>
    <message>
      <source>Logs</source>
      <translation>测井曲线</translation>
    </message>
    <message>
      <source>With data</source>
      <translation>有数据</translation>
    </message>
    <message>
      <source>water levels</source>
      <translation>水位</translation>
    </message>
    <message>
      <source>EM data (*.csv *.txt *.dat *.xyz);;TEMcompany XYZ (*.xyz);;All files (*)</source>
      <translation>EM 数据 (*.csv *.txt *.dat *.xyz);;TEMcompany XYZ (*.xyz);;所有文件 (*)</translation>
    </message>
    <message>
      <source>TEMcompany / TEM2Go</source>
      <translation>TEMcompany / TEM2Go</translation>
    </message>
    <message>
      <source>TEMcompany tTEM raw</source>
      <translation>TEMcompany tTEM 原始数据</translation>
    </message>
    <message>
      <source>Plan view</source>
      <translation>平面图</translation>
    </message>
    <message>
      <source>Plan-view uncertainty</source>
      <translation>平面不确定性</translation>
    </message>
    <message>
      <source>This format records no acquisition description; only a TEMcompany project carries one.</source>
      <translation>此格式不记录采集说明；只有 TEMcompany 工程包含该说明。</translation>
    </message>
    <message>
      <source>Volume view</source>
      <translation>体视图</translation>
    </message>
    <message>
      <source>Generic table</source>
      <translation>通用表格</translation>
    </message>
    <message>
      <source>Truncate the tail</source>
      <translation>截断尾部</translation>
    </message>
    <message>
      <source>Reject gates individually</source>
      <translation>逐个剔除时窗</translation>
    </message>
    <message>
      <source>transmitter loop</source>
      <translation>发射回线</translation>
    </message>
    <message>
      <source>receiver coil</source>
      <translation>接收线圈</translation>
    </message>
    <message>
      <source>Simultaneous</source>
      <translation>同步</translation>
    </message>
    <message>
      <source>TRF (formal, bound-aware)</source>
      <translation>TRF（正式，考虑边界约束）</translation>
    </message>
    <message>
      <source>Gauss-Newton (fast / legacy)</source>
      <translation>Gauss-Newton（快速 / 旧版）</translation>
    </message>
    <message>
      <source>EM sounding — FDEM: frequency, real, imag · TDEM: time, response.</source>
      <translation>EM 测深 — FDEM：频率、实部、虚部 · TDEM：时间、响应。</translation>
    </message>
    <message>
      <source>an FDEM inversion fits one field per frequency, and 'both' does not say which one the sounding holds. Choose 'secondary' or 'total'.</source>
      <translation>FDEM 反演对每个频率拟合一个场，而 'both' 并未说明测深数据包含的是哪一个。请选择 'secondary' 或 'total'。</translation>
    </message>
    <message>
      <source>unknown parameter</source>
      <translation>未知参数</translation>
    </message>
    <message>
      <source>Add to Project Map…</source>
      <translation>添加到工程地图…</translation>
    </message>
    <message>
      <source>Line section model (CSV)</source>
      <translation>测线断面模型 (CSV)</translation>
    </message>
    <message>
      <source>Recovered sounding model (CSV + npy)</source>
      <translation>反演得到的测深模型 (CSV + npy)</translation>
    </message>
    <message>
      <source>Run an inversion - one survey or a time-lapse series; Apply then corrects the model shown here, without inverting again.</source>
      <translation>运行反演——单次测量或时移序列；随后“应用”会校正此处显示的模型，无需重新反演。</translation>
    </message>
    <message>
      <source>Load ERT data to see how far each reading and its reciprocal disagree. In time-lapse mode the tab shows every survey of the list.</source>
      <translation>载入 ERT 数据以查看每个读数与其互易读数的差异程度。在时移模式下，该选项卡显示列表中的所有测量。</translation>
    </message>
    <message>
      <source>To get them, measure reciprocals in the field - each reading repeated with its current and potential electrodes exchanged; most instruments can add them to a protocol. For a survey written as two files, add the reciprocal file to the list as well and keep “Pair reciprocal files with their forward file” ticked.</source>
      <translation>要获得它们，请在野外进行互易测量——将每个读数的供电电极与测量电极互换后重复测量；大多数仪器可将其加入测量协议。对于以两个文件记录的测量，也请将互易文件加入列表，并保持勾选“将互易文件与其正向文件配对”。</translation>
    </message>
    <message>
      <source>Electrodes (*.csv *.txt *.dat);;All files (*)</source>
      <translation>电极 (*.csv *.txt *.dat);;所有文件 (*)</translation>
    </message>
    <message>
      <source>ERT data (*.dat *.ohm *.txt *.csv *.Data *.bin *.stg *.amp *.udf *.tab);;All files (*)</source>
      <translation>ERT 数据 (*.dat *.ohm *.txt *.csv *.Data *.bin *.stg *.amp *.udf *.tab);;所有文件 (*)</translation>
    </message>
    <message>
      <source>The inversion is done when one more iteration lowers χ² by less than this. Larger stops sooner; smaller makes sure the fit has really run out of room. A time-lapse run judges χ² over all its surveys.</source>
      <translation>当再迭代一次使 χ² 的下降量小于此值时，反演结束。值越大停止越早；值越小越能确保拟合确实已无改进空间。时移运行以所有测量的 χ² 进行判断。</translation>
    </message>
    <message>
      <source>Drop ERT data files or a folder here,
or choose the format and use Add files… on the right.</source>
      <translation>将 ERT 数据文件或文件夹拖放到此处，
或选择格式后使用右侧的“添加文件…”。</translation>
    </message>
    <message>
      <source>How survey times are read

1. From the file name. Put the year first:
      site_2026-01-12_05-50-38.dat   (recommended)
      site_2026_01_12_05_50_38.dat
      site_20260112_055038.dat
      site_2026-01-12T05-50-38.dat
2. Otherwise from a date line at the top of the file, e.g.
      # date: 2026-01-12 05:50:38
   (for BERT / pyGIMLi files: the very first line, before the electrode count).
3. Otherwise, if “Use file times” is ticked, from each file's modified time.

Avoid month-first or day-first names such as 01-12-2026: they can be read two
ways. Hover over a file to see where its time came from. Data format has more.</source>
      <translation>测量时间的读取方式

1. 从文件名读取。年份放在最前：
      site_2026-01-12_05-50-38.dat   （推荐）
      site_2026_01_12_05_50_38.dat
      site_20260112_055038.dat
      site_2026-01-12T05-50-38.dat
2. 否则从文件开头的日期行读取，例如
      # date: 2026-01-12 05:50:38
   （对于 BERT / pyGIMLi 文件：必须是第一行，位于电极数之前）。
3. 否则，若勾选了“使用文件时间”，则取每个文件的修改时间。

避免使用月份或日期在前的名称，例如 01-12-2026：它们可能有两种
解读方式。将鼠标悬停在文件上可查看其时间来源。更多信息见“数据格式”。</translation>
    </message>
    <message>
      <source>BERT / Unified (.ohm/.dat)</source>
      <translation>BERT / Unified (.ohm/.dat)</translation>
    </message>
    <message>
      <source>Syscal</source>
      <translation>Syscal</translation>
    </message>
    <message>
      <source>Protocol DC</source>
      <translation>DC 协议</translation>
    </message>
    <message>
      <source>Protocol IP</source>
      <translation>IP 协议</translation>
    </message>
    <message>
      <source>Sting / SuperSting</source>
      <translation>Sting / SuperSting</translation>
    </message>
    <message>
      <source>Sting</source>
      <translation>Sting</translation>
    </message>
    <message>
      <source>Lippmann</source>
      <translation>Lippmann</translation>
    </message>
    <message>
      <source>Electra</source>
      <translation>Electra</translation>
    </message>
    <message>
      <source>Subsurface Insights (.csv)</source>
      <translation>Subsurface Insights (.csv)</translation>
    </message>
    <message>
      <source>Subsurface Insights</source>
      <translation>Subsurface Insights</translation>
    </message>
    <message>
      <source>BGS PRIME / RESIMGR (.tab)</source>
      <translation>BGS PRIME / RESIMGR (.tab)</translation>
    </message>
    <message>
      <source>Custom</source>
      <translation>自定义</translation>
    </message>
    <message>
      <source>no measurements were parsed from it.</source>
      <translation>未从中解析出任何测量数据。</translation>
    </message>
    <message>
      <source>no measurement carries an apparent resistivity, and none could be rebuilt from the columns that were read.</source>
      <translation>没有任何测量值带有视电阻率，且无法根据已读取的列重建。</translation>
    </message>
    <message>
      <source>the measurements could not be matched to the electrode table.</source>
      <translation>测量数据无法与电极表匹配。</translation>
    </message>
    <message>
      <source>it defines no electrodes, so its quadrupoles cannot be placed. The Instrument setting is probably wrong for this file.</source>
      <translation>其中未定义电极，因此无法放置其四极组合。此文件的“仪器”设置可能有误。</translation>
    </message>
    <message>
      <source>pygimli is not installed, so the file can be plotted but not inverted.</source>
      <translation>未安装 pygimli，因此该文件可以绘图但无法反演。</translation>
    </message>
    <message>
      <source>10 µV, a common noise floor</source>
      <translation>10 µV，常见的噪声基底</translation>
    </message>
    <message>
      <source>0.1 mA, below which the injection failed</source>
      <translation>0.1 mA，低于此值视为供电失败</translation>
    </message>
    <message>
      <source>|V| floor</source>
      <translation>|V| 下限</translation>
    </message>
    <message>
      <source>Potential |V|</source>
      <translation>电位 |V|</translation>
    </message>
    <message>
      <source>|I| floor</source>
      <translation>|I| 下限</translation>
    </message>
    <message>
      <source>Current |I|</source>
      <translation>电流 |I|</translation>
    </message>
    <message>
      <source>ResIPy could not parse this file</source>
      <translation>ResIPy 无法解析此文件</translation>
    </message>
    <message>
      <source>not checked</source>
      <translation>未检查</translation>
    </message>
    <message>
      <source>Geometric factors were recomputed; see the log.</source>
      <translation>已重新计算几何因子；请查看日志。</translation>
    </message>
    <message>
      <source>Auto (this computer, then WSL)</source>
      <translation>自动（本机，其次 WSL）</translation>
    </message>
    <message>
      <source>This computer</source>
      <translation>本机</translation>
    </message>
    <message>
      <source>WSL (Windows)</source>
      <translation>WSL (Windows)</translation>
    </message>
    <message>
      <source>Write files only</source>
      <translation>仅写出文件</translation>
    </message>
    <message>
      <source>Auto (this computer)</source>
      <translation>自动（本机）</translation>
    </message>
    <message>
      <source>⚠ Geometric factors look wrong; the scale is off.</source>
      <translation>⚠ 几何因子似乎有误；标度存在偏差。</translation>
    </message>
    <message>
      <source>scale unverified</source>
      <translation>标度未核实</translation>
    </message>
    <message>
      <source>Load ERT data, or import a mesh, to see the inversion mesh.</source>
      <translation>载入 ERT 数据或导入网格以查看反演网格。</translation>
    </message>
    <message>
      <source>Quick: invert only</source>
      <translation>快速：仅反演</translation>
    </message>
    <message>
      <source>Thorough: check k, search λ</source>
      <translation>全面：检查 k，搜索 λ</translation>
    </message>
    <message>
      <source>In-house Gauss-Newton</source>
      <translation>内置 Gauss-Newton</translation>
    </message>
    <message>
      <source>PyGIMLi ERTManager</source>
      <translation>PyGIMLi ERTManager</translation>
    </message>
    <message>
      <source>ADTLERT 2.5D/3D (CUDA)</source>
      <translation>ADTLERT 2.5D/3D (CUDA)</translation>
    </message>
    <message>
      <source>E4D 3D (PNNL, external)</source>
      <translation>E4D 3D（PNNL，外部）</translation>
    </message>
    <message>
      <source>R2 2D (Binley, external)</source>
      <translation>R2 二维（Binley，外部程序）</translation>
    </message>
    <message>
      <source>R3t 3D (Binley, external)</source>
      <translation>R3t 三维（Binley，外部程序）</translation>
    </message>
    <message>
      <source>File err column</source>
      <translation>文件误差列</translation>
    </message>
    <message>
      <source>Estimate from the values below</source>
      <translation>根据下方数值估算</translation>
    </message>
    <message>
      <source>Larger of the two</source>
      <translation>取两者较大值</translation>
    </message>
    <message>
      <source>Stacking spread with the estimate</source>
      <translation>叠加排列及估计值</translation>
    </message>
    <message>
      <source>From the reciprocal error model</source>
      <translation>来自互易误差模型</translation>
    </message>
    <message>
      <source>No electrodes</source>
      <translation>无电极</translation>
    </message>
    <message>
      <source>Joint χ² over all time steps.</source>
      <translation>所有时间步的联合 χ²。</translation>
    </message>
    <message>
      <source>Run an inversion first.</source>
      <translation>请先运行反演。</translation>
    </message>
    <message>
      <source>Add an ERT data file to run an inversion.</source>
      <translation>添加 ERT 数据文件以运行反演。</translation>
    </message>
    <message>
      <source>E4D time-lapse: χ² of each survey in turn, the last one shown; each started from the solution before it.</source>
      <translation>E4D 时移：依次显示每次测量的 χ²，此处为最后一次；每次均以前一次的解为起点。</translation>
    </message>
    <message>
      <source>Pick the instrument / format, then add one file per survey. Name each file with its time, year first: site_2026-01-12_05-50-38.dat.</source>
      <translation>选择仪器/格式，然后每次测量添加一个文件。用时间命名每个文件，年份在前：site_2026-01-12_05-50-38.dat。</translation>
    </message>
    <message>
      <source>Run the time-lapse inversion first.</source>
      <translation>请先运行时移反演。</translation>
    </message>
    <message>
      <source>Add at least two surveys to the list for a time-lapse run - one file per survey, or drop a folder of them on the page.</source>
      <translation>时移运行需要在列表中至少添加两次测量——每次测量一个文件，或将存放这些文件的文件夹拖放到页面上。</translation>
    </message>
    <message>
      <source>Add displayed result to Project Map…</source>
      <translation>将显示的结果添加到工程地图…</translation>
    </message>
    <message>
      <source>Resistivity model (CSV + npy + mesh + VTK)</source>
      <translation>电阻率模型 (CSV + npy + 网格 + VTK)</translation>
    </message>
    <message>
      <source>Time-lapse results (CSV + npy + mesh + VTK + figures)</source>
      <translation>时移结果（CSV + npy + 网格 + VTK + 图件）</translation>
    </message>
    <message>
      <source>Electrode positions (CSV)</source>
      <translation>电极位置 (CSV)</translation>
    </message>
    <message>
      <source>Survey geometry (JSON)</source>
      <translation>测量几何 (JSON)</translation>
    </message>
    <message>
      <source>  Put the time in each file name, year first (e.g. &lt;code&gt;site_2026-01-12_05-50-38.dat&lt;/code&gt;), add a line &lt;code&gt;# date: 2026-01-12 05:50:38&lt;/code&gt; at the top of each file, or tick “Date undated files” below.</source>
      <translation>  在每个文件名中写入时间，年份在前（例如 &lt;code&gt;site_2026-01-12_05-50-38.dat&lt;/code&gt;），或在每个文件开头添加一行 &lt;code&gt;# date: 2026-01-12 05:50:38&lt;/code&gt;，或勾选下方的“为无日期文件指定日期”。</translation>
    </message>
    <message>
      <source># ERT → Water Content input format

Place an inverted-model bundle in one folder:

- `mesh_res.bms` - pyGIMLi inversion mesh
- `resmodel.npy` - inverted resistivity (n_cells, n_time)
- `index_marker.npy` - layer id per cell (n_cells)
- `all_coverage.npy` - coverage mask (n_time, n_cells), optional

See geo_input_format.md for details.</source>
      <translation># ERT → 含水量 输入格式

将反演模型数据包放在同一文件夹中：

- `mesh_res.bms` - pyGIMLi 反演网格
- `resmodel.npy` - 反演电阻率 (n_cells, n_time)
- `index_marker.npy` - 每个单元的层编号 (n_cells)
- `all_coverage.npy` - 覆盖度遮罩 (n_time, n_cells)，可选

详见 geo_input_format.md。</translation>
    </message>
    <message>
      <source>Target</source>
      <translation>目标</translation>
    </message>
    <message>
      <source>Parameters</source>
      <translation>参数</translation>
    </message>
    <message>
      <source>Porosity (where saturated)</source>
      <translation>孔隙度（饱和处）</translation>
    </message>
    <message>
      <source>Ready: check each layer's rock physics (3), then press Estimate water content.</source>
      <translation>就绪：检查每层的岩石物理参数 (3)，然后点击“估算含水量”。</translation>
    </message>
    <message>
      <source>Load an inverted ERT model (1) to estimate water content.</source>
      <translation>载入反演后的 ERT 模型 (1) 以估算含水量。</translation>
    </message>
    <message>
      <source>Tick at least one layer (2).</source>
      <translation>至少勾选一个层 (2)。</translation>
    </message>
    <message>
      <source>Tick what to estimate (4).</source>
      <translation>勾选要估算的内容 (4)。</translation>
    </message>
    <message>
      <source>Start by loading an inverted ERT model: use the example or open a folder.</source>
      <translation>首先载入反演后的 ERT 模型：使用示例或打开文件夹。</translation>
    </message>
    <message>
      <source>Next: tick at least one layer to estimate water content in (2, on the right).</source>
      <translation>下一步：至少勾选一个要估算含水量的层（右侧第 2 步）。</translation>
    </message>
    <message>
      <source>Next: tick what to estimate (4, on the right).</source>
      <translation>下一步：勾选要估算的内容（右侧第 4 步）。</translation>
    </message>
    <message>
      <source>Done: the maps are on the Results tab, and Time series follows two points through the surveys. Change the rock physics and estimate again to compare.</source>
      <translation>完成：地图位于“结果”选项卡，“时间序列”跟踪两个点在各次测量中的变化。可修改岩石物理参数并重新估算以进行比较。</translation>
    </message>
    <message>
      <source>Stopped by user</source>
      <translation>已被用户停止</translation>
    </message>
    <message>
      <source>&lt;h3&gt;GPR files this page reads&lt;/h3&gt;
&lt;ul&gt;
&lt;li&gt;&lt;b&gt;GSSI&lt;/b&gt; &lt;code&gt;.DZT&lt;/code&gt; (SIR-3000, SIR-4000, StructureScan, UtilityScan...).
Several channels: the first is read. A file recorded by time rather than by distance
has no trace spacing; set it under &lt;i&gt;Line geometry&lt;/i&gt;.&lt;/li&gt;
&lt;li&gt;&lt;b&gt;Sensors &amp;amp; Software pulseEKKO&lt;/b&gt; &lt;code&gt;.DT1&lt;/code&gt; with its &lt;code&gt;.HD&lt;/code&gt;
header beside it (open either).&lt;/li&gt;
&lt;li&gt;&lt;b&gt;MALA&lt;/b&gt; &lt;code&gt;.rd3&lt;/code&gt; or &lt;code&gt;.rd7&lt;/code&gt; with its &lt;code&gt;.rad&lt;/code&gt;
header beside it (open any of them).&lt;/li&gt;
&lt;li&gt;&lt;b&gt;SEG-Y&lt;/b&gt; &lt;code&gt;.sgy&lt;/code&gt; exported by GPR software. SEG-Y keeps the sample
interval in whole microseconds, so GPR exports write it in picoseconds; check the
time window it reports.&lt;/li&gt;
&lt;li&gt;&lt;code&gt;.npz&lt;/code&gt; saved by this page (&lt;i&gt;Save results&lt;/i&gt;).&lt;/li&gt;
&lt;/ul&gt;
&lt;p&gt;Ground elevations for a section in elevation: a CSV or text file of
&lt;code&gt;distance, elevation&lt;/code&gt; in metres, one row per point along the line.&lt;/p&gt;
</source>
      <translation>&lt;h3&gt;本页面可读取的 GPR 文件&lt;/h3&gt;
&lt;ul&gt;
&lt;li&gt;&lt;b&gt;GSSI&lt;/b&gt; &lt;code&gt;.DZT&lt;/code&gt;（SIR-3000、SIR-4000、StructureScan、UtilityScan...）。
多通道文件只读取第一个通道。按时间而非按距离记录的文件
没有道间距；请在&lt;i&gt;测线几何&lt;/i&gt;中设置。&lt;/li&gt;
&lt;li&gt;&lt;b&gt;Sensors &amp;amp; Software pulseEKKO&lt;/b&gt; &lt;code&gt;.DT1&lt;/code&gt;，旁边需有其 &lt;code&gt;.HD&lt;/code&gt;
头文件（打开任一个即可）。&lt;/li&gt;
&lt;li&gt;&lt;b&gt;MALA&lt;/b&gt; &lt;code&gt;.rd3&lt;/code&gt; 或 &lt;code&gt;.rd7&lt;/code&gt;，旁边需有其 &lt;code&gt;.rad&lt;/code&gt;
头文件（打开其中任一个即可）。&lt;/li&gt;
&lt;li&gt;由 GPR 软件导出的 &lt;b&gt;SEG-Y&lt;/b&gt; &lt;code&gt;.sgy&lt;/code&gt;。SEG-Y 以整微秒保存采样
间隔，因此 GPR 软件导出时以皮秒写入；请检查其报告的
时间窗口。&lt;/li&gt;
&lt;li&gt;本页面保存的 &lt;code&gt;.npz&lt;/code&gt;（&lt;i&gt;保存结果&lt;/i&gt;）。&lt;/li&gt;
&lt;/ul&gt;
&lt;p&gt;以高程显示断面所需的地面高程：一个 CSV 或文本文件，包含
&lt;code&gt;distance, elevation&lt;/code&gt;（单位为米），沿测线每点一行。&lt;/p&gt;
</translation>
    </message>
    <message>
      <source>Processed radargram</source>
      <translation>处理后的雷达剖面</translation>
    </message>
    <message>
      <source>Time</source>
      <translation>时间</translation>
    </message>
    <message>
      <source>the model's ground surface</source>
      <translation>模型的地表</translation>
    </message>
    <message>
      <source>As recorded</source>
      <translation>按原始记录</translation>
    </message>
    <message>
      <source>the simulated example GPR line</source>
      <translation>模拟的 GPR 示例测线</translation>
    </message>
    <message>
      <source>Processed GPR line, figure and recipe</source>
      <translation>处理后的 GPR 测线、图件和配方</translation>
    </message>
    <message>
      <source>Station data (*.csv *.txt *.dat);;All files (*)</source>
      <translation>测点数据 (*.csv *.txt *.dat);;所有文件 (*)</translation>
    </message>
    <message>
      <source>Linear (one solve per β)</source>
      <translation>线性（每个 β 求解一次）</translation>
    </message>
    <message>
      <source>SimPEG directives</source>
      <translation>SimPEG 指令</translation>
    </message>
    <message>
      <source>Add model to Project Map…</source>
      <translation>将模型添加到工程地图…</translation>
    </message>
    <message>
      <source>3D model (CSV + npz)</source>
      <translation>3D 模型（CSV + npz）</translation>
    </message>
    <message>
      <source>Observed</source>
      <translation>观测值</translation>
    </message>
    <message>
      <source>Regional</source>
      <translation>区域场</translation>
    </message>
    <message>
      <source>Residual</source>
      <translation>残差</translation>
    </message>
    <message>
      <source>Station file: three columns x, y, value (gravity mGal / magnetics nT).</source>
      <translation>测点文件：三列 x、y、数值（重力 mGal / 磁法 nT）。</translation>
    </message>
    <message>
      <source>Add product to Project Map…</source>
      <translation>将成果添加到工程地图…</translation>
    </message>
    <message>
      <source># Hydro input data format

Place these four files in one folder:

- `Watercontent.npy` - (n_time, n_layers, ny, nx) or (n_layers, ny, nx)
- `Porosity.npy` - (n_layers, ny, nx)
- `top.npy` - surface grid (ny, nx), NumPy
- `bot.npy` - layer bottoms (n_layers, ny, nx)

See hydro_input_format.md for details.</source>
      <translation># 水文输入数据格式

将以下四个文件放在同一文件夹中：

- `Watercontent.npy` - (n_time, n_layers, ny, nx) 或 (n_layers, ny, nx)
- `Porosity.npy` - (n_layers, ny, nx)
- `top.npy` - 地表网格 (ny, nx)，NumPy
- `bot.npy` - 各层底面 (n_layers, ny, nx)

详见 hydro_input_format.md。</translation>
    </message>
    <message>
      <source>Gravity</source>
      <translation>重力</translation>
    </message>
    <message>
      <source>Porosity</source>
      <translation>孔隙度</translation>
    </message>
    <message>
      <source>Saturation</source>
      <translation>饱和度</translation>
    </message>
    <message>
      <source>Profile</source>
      <translation>剖面</translation>
    </message>
    <message>
      <source>Methods</source>
      <translation>方法</translation>
    </message>
    <message>
      <source>Regolith</source>
      <translation>风化层</translation>
    </message>
    <message>
      <source>Fractured rock</source>
      <translation>裂隙岩体</translation>
    </message>
    <message>
      <source>Bedrock</source>
      <translation>基岩</translation>
    </message>
    <message>
      <source>Wenner</source>
      <translation>温纳</translation>
    </message>
    <message>
      <source>Schlumberger</source>
      <translation>施伦贝谢</translation>
    </message>
    <message>
      <source>Ready: the Section tab shows the ground under the line and where the sensors go. Press Simulate surveys.</source>
      <translation>就绪：“断面”选项卡显示测线下方的地层及传感器位置。点击“模拟测量”。</translation>
    </message>
    <message>
      <source>Load a hydrologic model (1) to simulate surveys.</source>
      <translation>载入水文模型 (1) 以模拟测量。</translation>
    </message>
    <message>
      <source>Draw a survey line on the map (2).</source>
      <translation>在地图上绘制一条测线 (2)。</translation>
    </message>
    <message>
      <source>Tick at least one survey (3).</source>
      <translation>至少勾选一次测量 (3)。</translation>
    </message>
    <message>
      <source>Simulating the surveys. This takes a minute or two.</source>
      <translation>正在模拟测量。这需要一两分钟。</translation>
    </message>
    <message>
      <source>Start by loading a hydrologic model: use the example or open a folder.</source>
      <translation>首先载入水文模型：使用示例或打开文件夹。</translation>
    </message>
    <message>
      <source>Next: click the start and then the end of a survey line on the map.</source>
      <translation>下一步：在地图上依次点击测线的起点和终点。</translation>
    </message>
    <message>
      <source>Next: tick the surveys to simulate (3, on the right).</source>
      <translation>下一步：勾选要模拟的测量（右侧第 3 步）。</translation>
    </message>
    <message>
      <source>Done: the results are on the Results tab. Change the line or the surveys and simulate again to compare.</source>
      <translation>完成：结果位于“结果”选项卡。可修改测线或测量并重新模拟以进行比较。</translation>
    </message>
    <message>
      <source>Volumetric water content</source>
      <translation>体积含水量</translation>
    </message>
    <message>
      <source>Synthetic data</source>
      <translation>合成数据</translation>
    </message>
    <message>
      <source>Now click the end of the survey line on the map.</source>
      <translation>现在在地图上点击测线的终点。</translation>
    </message>
    <message>
      <source>travel times</source>
      <translation>走时</translation>
    </message>
    <message>
      <source>Resistivity when saturated (Ω·m)</source>
      <translation>饱和时电阻率 (Ω·m)</translation>
    </message>
    <message>
      <source>Surface conductivity (S/m)</source>
      <translation>表面电导率 (S/m)</translation>
    </message>
    <message>
      <source>Mineral bulk modulus (GPa)</source>
      <translation>矿物体积模量 (GPa)</translation>
    </message>
    <message>
      <source>Mineral shear modulus (GPa)</source>
      <translation>矿物剪切模量 (GPa)</translation>
    </message>
    <message>
      <source>Mineral density (kg/m³)</source>
      <translation>矿物密度 (kg/m³)</translation>
    </message>
    <message>
      <source>Compatibility</source>
      <translation>兼容性</translation>
    </message>
    <message>
      <source>&lt;b&gt;Available in this release&lt;/b&gt;&lt;ul&gt;</source>
      <translation>&lt;b&gt;本版本可用&lt;/b&gt;&lt;ul&gt;</translation>
    </message>
    <message>
      <source>ERT data (*.dat *.ohm *.txt);;All files (*)</source>
      <translation>ERT 数据 (*.dat *.ohm *.txt);;所有文件 (*)</translation>
    </message>
    <message>
      <source>&lt;b&gt;Current observations&lt;/b&gt;&lt;ul&gt;</source>
      <translation>&lt;b&gt;当前观测&lt;/b&gt;&lt;ul&gt;</translation>
    </message>
    <message>
      <source>Travel-time data (*.dat *.sgt *.tt *.gtt *.txt);;All files (*)</source>
      <translation>走时数据 (*.dat *.sgt *.tt *.gtt *.txt);;所有文件 (*)</translation>
    </message>
    <message>
      <source>λ method A</source>
      <translation>λ 方法 A</translation>
    </message>
    <message>
      <source>λ method B</source>
      <translation>λ 方法 B</translation>
    </message>
    <message>
      <source>Cross-gradient λ A</source>
      <translation>交叉梯度 λ A</translation>
    </message>
    <message>
      <source>Cross-gradient λ B</source>
      <translation>交叉梯度 λ B</translation>
    </message>
    <message>
      <source>Velocity interface (m/s)</source>
      <translation>速度界面 (m/s)</translation>
    </message>
    <message>
      <source>Existing interface</source>
      <translation>现有界面</translation>
    </message>
    <message>
      <source>Solver backend</source>
      <translation>求解器后端</translation>
    </message>
    <message>
      <source>EM layers</source>
      <translation>EM 层</translation>
    </message>
    <message>
      <source>EM smoothness</source>
      <translation>EM 光滑度</translation>
    </message>
    <message>
      <source>FDEM weight</source>
      <translation>FDEM 权重</translation>
    </message>
    <message>
      <source>TDEM weight</source>
      <translation>TDEM 权重</translation>
    </message>
    <message>
      <source>Pairing tolerance (m; 0=auto)</source>
      <translation>配对容差 (m; 0=自动)</translation>
    </message>
    <message>
      <source>Potential-field lateral cells</source>
      <translation>位场横向单元数</translation>
    </message>
    <message>
      <source>Potential-field depth cells</source>
      <translation>位场深度方向单元数</translation>
    </message>
    <message>
      <source>Cross-gradient weight</source>
      <translation>交叉梯度权重</translation>
    </message>
    <message>
      <source>Gravity noise floor (mGal)</source>
      <translation>重力噪声下限 (mGal)</translation>
    </message>
    <message>
      <source>Magnetics noise floor (nT)</source>
      <translation>磁法噪声水平 (nT)</translation>
    </message>
    <message>
      <source>Regional detrend degree</source>
      <translation>区域去趋势阶数</translation>
    </message>
    <message>
      <source>Inducing field strength (nT)</source>
      <translation>感应场强度 (nT)</translation>
    </message>
    <message>
      <source>Inducing field inclination (°)</source>
      <translation>感应场倾角 (°)</translation>
    </message>
    <message>
      <source>Inducing field declination (°)</source>
      <translation>感应场偏角 (°)</translation>
    </message>
    <message>
      <source>Magnetics</source>
      <translation>磁法</translation>
    </message>
    <message>
      <source>Gravity weight</source>
      <translation>重力权重</translation>
    </message>
    <message>
      <source>Magnetics weight</source>
      <translation>磁法权重</translation>
    </message>
    <message>
      <source>&lt;h3&gt;Independent baseline comparison&lt;/h3&gt;&lt;ul&gt;</source>
      <translation>&lt;h3&gt;独立基准对比&lt;/h3&gt;&lt;ul&gt;</translation>
    </message>
    <message>
      <source>Add joint model to Project Map…</source>
      <translation>将联合模型添加到工程地图…</translation>
    </message>
    <message>
      <source>Joint models (CSV)</source>
      <translation>联合模型 (CSV)</translation>
    </message>
    <message>
      <source>EM tables (*.csv *.txt *.dat);;All files (*)</source>
      <translation>EM 表格 (*.csv *.txt *.dat);;所有文件 (*)</translation>
    </message>
    <message>
      <source>Spatial / geostatistical</source>
      <translation>空间 / 地统计</translation>
    </message>
    <message>
      <source>Balanced shared conductivity</source>
      <translation>均衡共享电导率</translation>
    </message>
    <message>
      <source>SimPEG cross-gradient</source>
      <translation>SimPEG 交叉梯度</translation>
    </message>
    <message>
      <source>Sequential structure constraint</source>
      <translation>顺序结构约束</translation>
    </message>
    <message>
      <source>Standard direct</source>
      <translation>标准直接法</translation>
    </message>
    <message>
      <source>Interactive 3D preview needs &lt;code&gt;pyvista&lt;/code&gt;, &lt;code&gt;pyvistaqt&lt;/code&gt; and a working &lt;code&gt;vtk&lt;/code&gt; build:&lt;br&gt;&lt;code&gt;pip install "pyhydrogeophysx[desktop-3d]"&lt;/code&gt;&lt;br&gt;&lt;br&gt;Install with whichever tool already manages the packages here, which is not always the one that created the environment. Run &lt;code&gt;conda list numpy&lt;/code&gt;: if it reports &lt;code&gt;pypi&lt;/code&gt;, use the pip command above; if it names a conda channel, use &lt;code&gt;conda install -c conda-forge pyvista pyvistaqt&lt;/code&gt; instead. Pulling VTK in through the other one leaves two builds in the same environment.&lt;br&gt;&lt;br&gt;Mesh generation and export still work without it.</source>
      <translation>交互式三维预览需要 &lt;code&gt;pyvista&lt;/code&gt;、&lt;code&gt;pyvistaqt&lt;/code&gt; 以及可正常工作的 &lt;code&gt;vtk&lt;/code&gt; 构建：&lt;br&gt;&lt;code&gt;pip install "pyhydrogeophysx[desktop-3d]"&lt;/code&gt;&lt;br&gt;&lt;br&gt;请使用当前管理这些包的工具进行安装，它不一定是创建该环境的工具。运行 &lt;code&gt;conda list numpy&lt;/code&gt;：若显示 &lt;code&gt;pypi&lt;/code&gt;，请使用上面的 pip 命令；若显示某个 conda 频道，请改用 &lt;code&gt;conda install -c conda-forge pyvista pyvistaqt&lt;/code&gt;。通过另一个工具引入 VTK 会在同一环境中留下两个构建版本。&lt;br&gt;&lt;br&gt;没有它，网格生成和导出仍可正常使用。</translation>
    </message>
    <message>
      <source>Mesh (*.vtk *.vtu *.vtp *.stl *.ply *.bms);;All files (*)</source>
      <translation>网格 (*.vtk *.vtu *.vtp *.stl *.ply *.bms);;所有文件 (*)</translation>
    </message>
    <message>
      <source>Sensor positions (*.csv *.txt *.dat *.xyz *.elec);;All files (*)</source>
      <translation>传感器位置 (*.csv *.txt *.dat *.xyz *.elec);;所有文件 (*)</translation>
    </message>
    <message>
      <source>E4D mesh configuration (*.cfg);;All files (*)</source>
      <translation>E4D 网格配置 (*.cfg);;所有文件 (*)</translation>
    </message>
    <message>
      <source>E4D / TetGen mesh (*.node *.ele);;All files (*)</source>
      <translation>E4D / TetGen 网格 (*.node *.ele);;所有文件 (*)</translation>
    </message>
    <message>
      <source>No configuration loaded: the layout is built from steps 1, 3 and 4.</source>
      <translation>未载入配置：布局由第 1、3、4 步构建。</translation>
    </message>
    <message>
      <source>Surface grid</source>
      <translation>地表网格</translation>
    </message>
    <message>
      <source>Single borehole</source>
      <translation>单孔</translation>
    </message>
    <message>
      <source>Crosshole</source>
      <translation>跨孔</translation>
    </message>
    <message>
      <source>Surface with topography</source>
      <translation>带地形的地表</translation>
    </message>
    <message>
      <source>Box mesh</source>
      <translation>长方体网格</translation>
    </message>
    <message>
      <source>Flat</source>
      <translation>平坦</translation>
    </message>
    <message>
      <source>Linear tilt</source>
      <translation>线性倾斜</translation>
    </message>
    <message>
      <source>Gaussian hill</source>
      <translation>高斯山丘</translation>
    </message>
    <message>
      <source>Custom expression</source>
      <translation>自定义表达式</translation>
    </message>
    <message>
      <source>From file (x, y, z)</source>
      <translation>来自文件 (x, y, z)</translation>
    </message>
    <message>
      <source>Gmsh (tetrahedral)</source>
      <translation>Gmsh（四面体）</translation>
    </message>
    <message>
      <source>PyGIMLi prism</source>
      <translation>PyGIMLi 棱柱体</translation>
    </message>
    <message>
      <source>Structured grid</source>
      <translation>结构化网格</translation>
    </message>
    <message>
      <source>Neither TetGen nor Gmsh is installed: pip install tetgen.</source>
      <translation>TetGen 和 Gmsh 均未安装：pip install tetgen。</translation>
    </message>
    <message>
      <source>A structured PyGIMLi grid, with a node at every sensor and a flat top.</source>
      <translation>结构化 PyGIMLi 网格，每个传感器处有一个节点，顶面平坦。</translation>
    </message>
    <message>
      <source>TetGen is not installed, so Gmsh stands in (pip install tetgen for E4D's own mesher).</source>
      <translation>TetGen 未安装，因此改用 Gmsh（pip install tetgen 以使用 E4D 自带的网格生成器）。</translation>
    </message>
    <message>
      <source>The ground surface is triangulated, then TetGen fills a fine zone around the electrodes, with a refinement point beside each buried one, inside an outer zone reaching far enough for the boundary conditions not to matter. The E4D .cfg and .poly are saved with the mesh, so E4D can run on the same geometry.</source>
      <translation>先对地表进行三角剖分，然后 TetGen 在电极周围填充精细区（每个埋设电极旁设置一个加密点），其外是一个延伸足够远、使边界条件不再产生影响的外部区域。E4D 的 .cfg 和 .poly 会与网格一起保存，因此 E4D 可在相同几何上运行。</translation>
    </message>
    <message>
      <source>Gmsh tetrahedra, graded from the sensors outward, in a box with a flat top; the structured grid stands in when Gmsh is missing or fails.</source>
      <translation>Gmsh 四面体网格，从传感器向外渐变，位于顶面平坦的长方体中；Gmsh 缺失或失败时改用结构化网格。</translation>
    </message>
    <message>
      <source>The prism mesh needs sensors on the surface and a domain with topography, so a structured grid is built instead.</source>
      <translation>棱柱网格需要传感器位于地表且区域带地形，因此改为构建结构化网格。</translation>
    </message>
    <message>
      <source>Auto: a structured PyGIMLi grid, with a node at every sensor and a flat top; the prism mesh is for sensors on the surface with topography.</source>
      <translation>自动：结构化 PyGIMLi 网格，每个传感器处有一个节点，顶面平坦；棱柱网格适用于位于带地形地表上的传感器。</translation>
    </message>
    <message>
      <source>A fine zone the padding beyond the electrodes, inside an outer zone out to the boundary distance and down to the mesh bottom.</source>
      <translation>精细区覆盖电极以外的扩展范围，其外包裹一个延伸至边界距离、向下直至网格底部的外部区域。</translation>
    </message>
    <message>
      <source>A box from the origin, of the size below, with a flat top.</source>
      <translation>从原点起、尺寸如下的平顶长方体。</translation>
    </message>
    <message>
      <source>A block with a flat top around the sensors, padded as below.</source>
      <translation>围绕传感器的平顶块体，按下方设置向外扩展。</translation>
    </message>
    <message>
      <source>The mesh top follows the ground below.</source>
      <translation>网格顶面沿下方地面起伏。</translation>
    </message>
    <message>
      <source>This mesh has a flat top at the highest sensor; the prism engine follows the ground through them.</source>
      <translation>此网格的顶面平坦，位于最高传感器处；棱柱引擎会贴合穿过各传感器的地面。</translation>
    </message>
    <message>
      <source>The sensors are placed on the ground below, but this mesh has a flat top at the highest of them; the prism engine follows the ground.</source>
      <translation>传感器放置在下方地面上，但此网格的顶面平坦，位于其中最高者的高度；棱柱引擎会贴合地面。</translation>
    </message>
    <message>
      <source>Each zone takes the cells whose centre lies inside it, so its faces are only as sharp as the cells there.</source>
      <translation>每个分区包含中心位于其内的单元，因此其边界的清晰程度取决于该处单元的大小。</translation>
    </message>
    <message>
      <source>Load mesh…</source>
      <translation>载入网格…</translation>
    </message>
    <message>
      <source>Open E4D mesh…</source>
      <translation>打开 E4D 网格…</translation>
    </message>
    <message>
      <source>View a mesh E4D (or TetGen) built: the .1.node / .1.ele files, with the .trn beside them putting it back in survey coordinates.</source>
      <translation>查看 E4D（或 TetGen）生成的网格：.1.node / .1.ele 文件，并借助同目录下的 .trn 文件将其变换回测量坐标。</translation>
    </message>
    <message>
      <source>Axes</source>
      <translation>坐标轴</translation>
    </message>
    <message>
      <source>Sensors</source>
      <translation>传感器</translation>
    </message>
    <message>
      <source>First sensor at</source>
      <translation>首个传感器位于</translation>
    </message>
    <message>
      <source>Borehole at</source>
      <translation>钻孔位于</translation>
    </message>
    <message>
      <source>Sensors from z</source>
      <translation>按 z 确定传感器</translation>
    </message>
    <message>
      <source>Sensors / borehole</source>
      <translation>传感器 / 钻孔</translation>
    </message>
    <message>
      <source>Positions</source>
      <translation>位置</translation>
    </message>
    <message>
      <source>Surface sensors</source>
      <translation>地表电极</translation>
    </message>
    <message>
      <source>First at</source>
      <translation>首个位于</translation>
    </message>
    <message>
      <source>Surface z</source>
      <translation>地表 z</translation>
    </message>
    <message>
      <source>Borehole sensors</source>
      <translation>钻孔电极</translation>
    </message>
    <message>
      <source>Auto (TetGen, else Gmsh)</source>
      <translation>自动（TetGen，否则 Gmsh）</translation>
    </message>
    <message>
      <source>Gmsh</source>
      <translation>Gmsh</translation>
    </message>
    <message>
      <source>Surface elevation</source>
      <translation>地表高程</translation>
    </message>
    <message>
      <source>Base elevation</source>
      <translation>底面高程</translation>
    </message>
    <message>
      <source>Slope</source>
      <translation>坡度</translation>
    </message>
    <message>
      <source>Base z</source>
      <translation>底面 z</translation>
    </message>
    <message>
      <source>Width sigma</source>
      <translation>宽度 σ</translation>
    </message>
    <message>
      <source>Centre at</source>
      <translation>中心位于</translation>
    </message>
    <message>
      <source>E4D meshes no box: it builds on flat ground at the elevation below. Pick Surface with topography for any other ground.</source>
      <translation>E4D 不生成长方体网格：它在下方所设高程的平坦地面上构建。其他任何地面请选择“带地形的地表”。</translation>
    </message>
    <message>
      <source>The loaded E4D configuration defines its own zones, so these are not used; clear it (✕) to build from the sensor array with them.</source>
      <translation>已载入的 E4D 配置定义了自己的分区，因此不使用这些分区；清除该配置 (✕) 后可基于电极阵列并使用这些分区构建。</translation>
    </message>
    <message>
      <source>Marker</source>
      <translation>标记</translation>
    </message>
    <message>
      <source>Attribute</source>
      <translation>属性</translation>
    </message>
    <message>
      <source>Mesher</source>
      <translation>网格剖分器</translation>
    </message>
    <message>
      <source>TetGen path</source>
      <translation>TetGen 路径</translation>
    </message>
    <message>
      <source>Starting conductivity</source>
      <translation>初始电导率</translation>
    </message>
    <message>
      <source>Investigation depth</source>
      <translation>探测深度</translation>
    </message>
    <message>
      <source>Boundary extension</source>
      <translation>边界扩展</translation>
    </message>
    <message>
      <source>Length (x)</source>
      <translation>长度 (x)</translation>
    </message>
    <message>
      <source>Width (y)</source>
      <translation>宽度 (y)</translation>
    </message>
    <message>
      <source>Depth (z)</source>
      <translation>深度 (z)</translation>
    </message>
    <message>
      <source>Lateral padding</source>
      <translation>横向扩边</translation>
    </message>
    <message>
      <source>Top padding</source>
      <translation>顶部扩展</translation>
    </message>
    <message>
      <source>Bottom padding</source>
      <translation>底部扩展</translation>
    </message>
    <message>
      <source>Fine zone padding</source>
      <translation>精细区外扩</translation>
    </message>
    <message>
      <source>Below deepest electrode</source>
      <translation>最深电极以下</translation>
    </message>
    <message>
      <source>Outer boundary distance</source>
      <translation>外边界距离</translation>
    </message>
    <message>
      <source>Mesh bottom depth</source>
      <translation>网格底部深度</translation>
    </message>
    <message>
      <source>Sensor refinement</source>
      <translation>电极加密</translation>
    </message>
    <message>
      <source>Attractor distance</source>
      <translation>吸引距离</translation>
    </message>
    <message>
      <source>Boundary refinement</source>
      <translation>边界加密</translation>
    </message>
    <message>
      <source>Fine layer dz</source>
      <translation>细分层 dz</translation>
    </message>
    <message>
      <source>Coarse layer dz</source>
      <translation>粗层 dz</translation>
    </message>
    <message>
      <source>Horizontal cell</source>
      <translation>水平单元</translation>
    </message>
    <message>
      <source>Vertical cell</source>
      <translation>垂直单元</translation>
    </message>
    <message>
      <source>Fine zone element volume</source>
      <translation>精细区单元体积</translation>
    </message>
    <message>
      <source>Quality (radius-edge)</source>
      <translation>质量（半径-边长比）</translation>
    </message>
    <message>
      <source>Electrode refinement</source>
      <translation>电极加密</translation>
    </message>
    <message>
      <source>⬤ Unsaved (this session)</source>
      <translation>⬤ 未保存（本次会话）</translation>
    </message>
    <message>
      <source>Succeeded</source>
      <translation>成功</translation>
    </message>
    <message>
      <source>Failed</source>
      <translation>失败</translation>
    </message>
    <message>
      <source>Cancelled</source>
      <translation>已取消</translation>
    </message>
    <message>
      <source>Interrupted</source>
      <translation>已中断</translation>
    </message>
    <message>
      <source>Incomplete</source>
      <translation>未完成</translation>
    </message>
    <message>
      <source>Needs review</source>
      <translation>需要复核</translation>
    </message>
    <message>
      <source>Running</source>
      <translation>运行中</translation>
    </message>
    <message>
      <source>Unknown</source>
      <translation>未知</translation>
    </message>
    <message>
      <source>No runs in this Project yet. Run a computation from any module; it appears here under “Unsaved” until you save it to the Project.</source>
      <translation>此工程中尚无运行记录。从任一模块运行计算后，它会显示在此处的“未保存”下，直到你将其保存到工程中。</translation>
    </message>
    <message>
      <source>&lt;table cellspacing="0" cellpadding="3"&gt;</source>
      <translation>&lt;table cellspacing="0" cellpadding="3"&gt;</translation>
    </message>
    <message>
      <source>Current Project</source>
      <translation>当前工程</translation>
    </message>
    <message>
      <source>Show the Project that new computations are written to.</source>
      <translation>显示新计算结果写入的工程。</translation>
    </message>
    <message>
      <source>Browse Other Project…</source>
      <translation>浏览其他工程…</translation>
    </message>
    <message>
      <source>Open another Project folder read-only, without changing where results are written.</source>
      <translation>以只读方式打开另一个工程文件夹，不改变结果的写入位置。</translation>
    </message>
    <message>
      <source>Open this Project folder in the system file manager.</source>
      <translation>在系统文件管理器中打开此工程文件夹。</translation>
    </message>
    <message>
      <source>Re-read the run history from disk.</source>
      <translation>从磁盘重新读取运行历史。</translation>
    </message>
    <message>
      <source>All statuses</source>
      <translation>所有状态</translation>
    </message>
    <message>
      <source>This folder contains GeoSAGE models. To view them, choose View results in Data &amp; reports. Use a separate Project to save your work.</source>
      <translation>此文件夹包含 GeoSAGE 模型。要查看它们，请在“数据与报告”中选择“查看结果”。请使用单独的工程保存你的工作。</translation>
    </message>
    <message>
      <source>Module</source>
      <translation>模块</translation>
    </message>
    <message>
      <source>Operation</source>
      <translation>操作</translation>
    </message>
    <message>
      <source>Started</source>
      <translation>已开始</translation>
    </message>
    <message>
      <source>Run ID</source>
      <translation>运行 ID</translation>
    </message>
    <message>
      <source>Fixed-λ resistivity model</source>
      <translation>固定 λ 电阻率模型</translation>
    </message>
    <message>
      <source>Open a saved model result in the Visualization tab first.</source>
      <translation>请先在“可视化”选项卡中打开已保存的模型结果。</translation>
    </message>
    <message>
      <source>This run corrected its own sections and its uncorrected models are missing, so they cannot be corrected again.</source>
      <translation>此运行已校正自身断面，且缺少未校正的模型，因此无法再次校正。</translation>
    </message>
    <message>
      <source>Provide 'run' (an id or a label).</source>
      <translation>请提供 'run'（ID 或标签）。</translation>
    </message>
    <message>
      <source>Origin</source>
      <translation>原点</translation>
    </message>
    <message>
      <source>Imported in place from an existing results folder</source>
      <translation>从已有结果文件夹原位导入</translation>
    </message>
    <message>
      <source>Survey measured</source>
      <translation>实测数据</translation>
    </message>
    <message>
      <source>MT time series (*.bin *.td_* *.ats *.z3d *.Z3D *.tbl *.TBL *.txt *.TXT);;All files (*)</source>
      <translation>MT 时间序列 (*.bin *.td_* *.ats *.z3d *.Z3D *.tbl *.TBL *.txt *.TXT);;所有文件 (*)</translation>
    </message>
    <message>
      <source>MT transfer functions (*.edi *.EDI *.xml *.zss *.zrr *.zmm *.j);;All files (*)</source>
      <translation>MT 传递函数 (*.edi *.EDI *.xml *.zss *.zrr *.zmm *.j);;所有文件 (*)</translation>
    </message>
    <message>
      <source>TEM sounding (*.csv *.txt *.dat *.npz);;All files (*)</source>
      <translation>TEM 测深 (*.csv *.txt *.dat *.npz);;所有文件 (*)</translation>
    </message>
    <message>
      <source>1D model</source>
      <translation>1D 模型</translation>
    </message>
    <message>
      <source>Dimensionality</source>
      <translation>维性</translation>
    </message>
    <message>
      <source>Phase tensors</source>
      <translation>相位张量</translation>
    </message>
    <message>
      <source>2D section</source>
      <translation>2D 断面</translation>
    </message>
    <message>
      <source>Sites and data quality</source>
      <translation>测站与数据质量</translation>
    </message>
    <message>
      <source>Hx</source>
      <translation>Hx</translation>
    </message>
    <message>
      <source>Hy</source>
      <translation>Hy</translation>
    </message>
    <message>
      <source>Hz</source>
      <translation>Hz</translation>
    </message>
    <message>
      <source>50 Hz</source>
      <translation>50 Hz</translation>
    </message>
    <message>
      <source>60 Hz</source>
      <translation>60 Hz</translation>
    </message>
    <message>
      <source>det(Z) - rotation invariant</source>
      <translation>det(Z) - 旋转不变量</translation>
    </message>
    <message>
      <source>Zxy and Zyx together</source>
      <translation>Zxy 与 Zyx 联合</translation>
    </message>
    <message>
      <source>Φmin (°)</source>
      <translation>Φmin (°)</translation>
    </message>
    <message>
      <source>Skew β (°)</source>
      <translation>偏度 β (°)</translation>
    </message>
    <message>
      <source>Φmax (°)</source>
      <translation>Φmax (°)</translation>
    </message>
    <message>
      <source>TE + TM</source>
      <translation>TE + TM</translation>
    </message>
    <message>
      <source>TE only</source>
      <translation>仅 TE</translation>
    </message>
    <message>
      <source>TM only</source>
      <translation>仅 TM</translation>
    </message>
    <message>
      <source>Open a recording folder (Phoenix, Metronix, Zonge, LEMI) or add EDI / EMTF XML sites.</source>
      <translation>打开记录文件夹（Phoenix、Metronix、Zonge、LEMI）或添加 EDI / EMTF XML 测点。</translation>
    </message>
    <message>
      <source>Sites and models (EDI, XML, CSV)</source>
      <translation>测点与模型 (EDI, XML, CSV)</translation>
    </message>
    <message>
      <source>listed in the assistant panel</source>
      <translation>列于助手面板中</translation>
    </message>
    <message>
      <source>A workflow is already running. Follow its progress in the center or use Stop.</source>
      <translation>已有工作流正在运行。可在中间区域查看进度，或使用“停止”。</translation>
    </message>
    <message>
      <source>Add your data in the Workflow page, then send “continue” here. I have kept your goal.</source>
      <translation>请在工作流页面添加数据，然后在此发送“continue”。我已保留你的目标。</translation>
    </message>
    <message>
      <source>Process the supplied configuration or results and summarize the numerical evidence without AI.</source>
      <translation>处理所提供的配置或结果，并在不使用 AI 的情况下汇总数值依据。</translation>
    </message>
    <message>
      <source>Read the report</source>
      <translation>阅读报告</translation>
    </message>
    <message>
      <source>File classification ready. Review/edit the roles in Workflow, then send “continue”. Unknown files must be assigned or ignored.</source>
      <translation>文件分类已就绪。请在工作流中检查/编辑角色，然后发送“continue”。未知文件必须指定角色或忽略。</translation>
    </message>
    <message>
      <source>Move survey up</source>
      <translation>上移测量</translation>
    </message>
    <message>
      <source>Move survey down</source>
      <translation>下移测量</translation>
    </message>
    <message>
      <source>Select one file for this role, or a role that takes several files in order.</source>
      <translation>为此角色选择一个文件，或选择一个按顺序接收多个文件的角色。</translation>
    </message>
    <message>
      <source>Open run folder</source>
      <translation>打开运行文件夹</translation>
    </message>
    <message>
      <source>Replay this run</source>
      <translation>回放此运行</translation>
    </message>
    <message>
      <source>Show raw log</source>
      <translation>显示原始日志</translation>
    </message>
    <message>
      <source>The run was stopped before it finished; partial files remain in the output folder.</source>
      <translation>运行未完成即已停止；部分文件保留在输出文件夹中。</translation>
    </message>
    <message>
      <source>Numerical results ready · AI interpretation not run</source>
      <translation>数值结果已就绪 · 未运行 AI 解释</translation>
    </message>
    <message>
      <source>Choose a slice and method, then click Interpolate to draw a smooth map.
Kriging fits a semivariogram and reports its own variance; the other
methods are deterministic. Resistivity is interpolated in log space.
Cells outside the convex hull of the stations are always blanked.</source>
      <translation>选择切片和方法，然后点击“插值”绘制平滑地图。
克里金法拟合半变异函数并给出其自身的方差；其他
方法均为确定性方法。电阻率在对数空间中插值。
测点凸包以外的单元始终置空。</translation>
    </message>
    <message>
      <source>Points only</source>
      <translation>仅点</translation>
    </message>
    <message>
      <source>Kriging (ordinary)</source>
      <translation>克里金（普通）</translation>
    </message>
    <message>
      <source>Inverse distance</source>
      <translation>反距离</translation>
    </message>
    <message>
      <source>Linear (triangulation)</source>
      <translation>线性（三角剖分）</translation>
    </message>
    <message>
      <source>Cubic (triangulation)</source>
      <translation>三次（三角剖分）</translation>
    </message>
    <message>
      <source>Nearest neighbour</source>
      <translation>最近邻</translation>
    </message>
    <message>
      <source>Thin-plate spline</source>
      <translation>薄板样条</translation>
    </message>
    <message>
      <source>This slice has no values to interpolate; the note below the map says why.</source>
      <translation>此切片没有可插值的数值；地图下方的说明给出了原因。</translation>
    </message>
    <message>
      <source>Select a survey in the list to map its values.</source>
      <translation>在列表中选择一次测量，将其数值成图。</translation>
    </message>
    <message>
      <source>Wells have no plan slice; click one to compare it with the surveys around it.</source>
      <translation>钻孔没有平面切片；点击某个钻孔可将其与周围的测量进行比较。</translation>
    </message>
    <message>
      <source>Choose a data slice to map, then an interpolation method under Surface.</source>
      <translation>选择要成图的数据切片，然后在“曲面”下选择插值方法。</translation>
    </message>
    <message>
      <source>Choose an interpolation method under Surface to grid this slice.</source>
      <translation>在“曲面”下选择插值方法，以对该切片进行网格化。</translation>
    </message>
    <message>
      <source>All methods</source>
      <translation>所有方法</translation>
    </message>
    <message>
      <source>Rename</source>
      <translation>重命名</translation>
    </message>
    <message>
      <source>Add available result…</source>
      <translation>添加可用结果…</translation>
    </message>
    <message>
      <source>Import point product CSV…</source>
      <translation>导入点数据成果 CSV…</translation>
    </message>
    <message>
      <source>Resistivity (Ω·m); below DOI hidden</source>
      <translation>电阻率 (Ω·m)；DOI 以下隐藏</translation>
    </message>
    <message>
      <source>Current project map (PNG)</source>
      <translation>当前工程地图 (PNG)</translation>
    </message>
    <message>
      <source>Interpolated plan grid (ASCII / CSV)</source>
      <translation>插值平面网格 (ASCII / CSV)</translation>
    </message>
    <message>
      <source>Provide 'survey' (an id or a name).</source>
      <translation>请提供 'survey'（ID 或名称）。</translation>
    </message>
    <message>
      <source>the project map could not be read</source>
      <translation>无法读取工程地图</translation>
    </message>
    <message>
      <source># Seismic → Structure input format

Add one or more 2D seismic velocity lines. Each line needs:

- a pyGIMLi mesh (`velmesh.bms`)
- a per-cell velocity array (`Vinvmodel.npy`)
- map coordinates of the line endpoints (x0, y0) → (x1, y1)

See seismic3d_input_format.md for details.</source>
      <translation># 地震 → 结构 输入格式

添加一条或多条二维地震速度测线。每条测线需要：

- 一个 pyGIMLi 网格（`velmesh.bms`）
- 逐单元速度数组（`Vinvmodel.npy`）
- 测线端点的地图坐标 (x0, y0) → (x1, y1)

详见 seismic3d_input_format.md。</translation>
    </message>
    <message>
      <source>Lines</source>
      <translation>测线</translation>
    </message>
    <message>
      <source>Structure</source>
      <translation>结构</translation>
    </message>
    <message>
      <source>Grid</source>
      <translation>网格</translation>
    </message>
    <message>
      <source>Build</source>
      <translation>构建</translation>
    </message>
    <message>
      <source>Start x</source>
      <translation>起始 x</translation>
    </message>
    <message>
      <source>Start y</source>
      <translation>起始 y</translation>
    </message>
    <message>
      <source>End x</source>
      <translation>终点 x</translation>
    </message>
    <message>
      <source>End y</source>
      <translation>终点 y</translation>
    </message>
    <message>
      <source>Add a seismic line to see its velocity section.</source>
      <translation>添加一条地震测线以查看其速度断面。</translation>
    </message>
    <message>
      <source>Ready: check the bedrock top on each line's Section (2), then press Build 3D model.</source>
      <translation>就绪：在每条测线的断面 (2) 上检查基岩顶面，然后点击“构建三维模型”。</translation>
    </message>
    <message>
      <source>Add at least one seismic line (1) to build a 3D model.</source>
      <translation>至少添加一条地震测线 (1) 以构建三维模型。</translation>
    </message>
    <message>
      <source>Building the 3D model: interpolating the velocity between the lines. This can take a few minutes.</source>
      <translation>正在构建三维模型：在测线之间插值速度。这可能需要几分钟。</translation>
    </message>
    <message>
      <source>Start by adding seismic lines: use the example or add a line.</source>
      <translation>首先添加地震测线：使用示例或添加一条测线。</translation>
    </message>
    <message>
      <source>One line gives the 3D model no width: add the others (1), placing each by its two ends, then press Build 3D model.</source>
      <translation>仅一条测线无法为三维模型提供宽度：请添加其他测线 (1)，按两个端点放置每条测线，然后点击“构建三维模型”。</translation>
    </message>
    <message>
      <source>Seismic (*.sgy *.segy *.dat *.sg2 *.seg2 *.npy *.npz *.csv *.txt);;SEG-Y (*.sgy *.segy);;Geometrics DAT (*.dat);;SEG-2 (*.sg2 *.seg2);;Array (*.npy *.npz *.csv *.txt);;All files (*)</source>
      <translation>地震数据 (*.sgy *.segy *.dat *.sg2 *.seg2 *.npy *.npz *.csv *.txt);;SEG-Y (*.sgy *.segy);;Geometrics DAT (*.dat);;SEG-2 (*.sg2 *.seg2);;数组 (*.npy *.npz *.csv *.txt);;所有文件 (*)</translation>
    </message>
    <message>
      <source>Inversion source: picks (none yet).</source>
      <translation>反演来源：拾取（尚无）。</translation>
    </message>
    <message>
      <source>Auto-pick could not start; see the log.</source>
      <translation>无法启动自动拾取；请查看日志。</translation>
    </message>
    <message>
      <source>The shots are already being picked.</source>
      <translation>各炮已在拾取中。</translation>
    </message>
    <message>
      <source>A stack is already running.</source>
      <translation>已有叠加正在运行。</translation>
    </message>
    <message>
      <source>Shot timing left as recorded.</source>
      <translation>炮点时间保持原记录。</translation>
    </message>
    <message>
      <source>Not checked: too few traces to test for flat events</source>
      <translation>未检查：道数太少，无法检测水平同相轴</translation>
    </message>
    <message>
      <source>No reflection confirmed: no event stays flat across the offsets</source>
      <translation>未确认反射：没有同相轴在各偏移距上保持水平</translation>
    </message>
    <message>
      <source>The stack was stopped before it finished.</source>
      <translation>叠加在完成前已被停止。</translation>
    </message>
    <message>
      <source>the records' geophones differ; all are placed as the first record's</source>
      <translation>各记录的检波器不同；全部按第一个记录的位置放置</translation>
    </message>
    <message>
      <source>Every shot is picked — say 'continue' to run the SRT inversion.</source>
      <translation>所有炮均已拾取——发送 'continue' 以运行 SRT 反演。</translation>
    </message>
    <message>
      <source>PyGIMLi TravelTimeManager</source>
      <translation>PyGIMLi TravelTimeManager</translation>
    </message>
    <message>
      <source>the spread moves along the line between records</source>
      <translation>排列在各记录之间沿测线移动</translation>
    </message>
    <message>
      <source>The picker no longer uses an STA/LTA ratio; set pick_threshold (a fraction of each trace's peak, default 0.2) instead.</source>
      <translation>拾取器不再使用 STA/LTA 比值；请改为设置 pick_threshold（每道峰值的比例，默认 0.2）。</translation>
    </message>
    <message>
      <source>Velocity model (CSV + npy + mesh + VTK)</source>
      <translation>速度模型（CSV + npy + 网格 + VTK）</translation>
    </message>
    <message>
      <source>First-arrival picks (CSV)</source>
      <translation>初至拾取 (CSV)</translation>
    </message>
    <message>
      <source>Travel-time container (PyGIMLi .dat)</source>
      <translation>走时数据容器 (PyGIMLi .dat)</translation>
    </message>
    <message>
      <source>excluded record</source>
      <translation>已排除的记录</translation>
    </message>
    <message>
      <source>in the shots left out</source>
      <translation>在留出的炮中</translation>
    </message>
    <message>
      <source>early energy</source>
      <translation>早期能量</translation>
    </message>
    <message>
      <source>with early signal</source>
      <translation>含早期信号</translation>
    </message>
    <message>
      <source>  (main thread frame unavailable)</source>
      <translation>  （主线程帧不可用）</translation>
    </message>
    <message>
      <source>Default folder</source>
      <translation>默认文件夹</translation>
    </message>
    <message>
      <source>Segoe UI</source>
      <translation>Segoe UI</translation>
    </message>
    <message>
      <source>PingFang SC</source>
      <translation>PingFang SC</translation>
    </message>
    <message>
      <source>Hiragino Sans GB</source>
      <translation>Hiragino Sans GB</translation>
    </message>
    <message>
      <source>Microsoft YaHei</source>
      <translation>Microsoft YaHei</translation>
    </message>
    <message>
      <source>Noto Sans CJK SC</source>
      <translation>Noto Sans CJK SC</translation>
    </message>
    <message>
      <source>Helvetica Neue</source>
      <translation>Helvetica Neue</translation>
    </message>
    <message>
      <source>Arial</source>
      <translation>Arial</translation>
    </message>
    <message>
      <source>DejaVu Sans</source>
      <translation>DejaVu Sans</translation>
    </message>
    <message>
      <source>SF Mono</source>
      <translation>SF Mono</translation>
    </message>
    <message>
      <source>Menlo</source>
      <translation>Menlo</translation>
    </message>
    <message>
      <source>Consolas</source>
      <translation>Consolas</translation>
    </message>
    <message>
      <source>DejaVu Sans Mono</source>
      <translation>DejaVu Sans Mono</translation>
    </message>
    <message>
      <source>Courier New</source>
      <translation>Courier New</translation>
    </message>
    <message>
      <source>Heiti SC</source>
      <translation>Heiti SC</translation>
    </message>
    <message>
      <source>Songti SC</source>
      <translation>Songti SC</translation>
    </message>
    <message>
      <source>Arial Unicode MS</source>
      <translation>Arial Unicode MS</translation>
    </message>
    <message>
      <source>Source Han Sans SC</source>
      <translation>Source Han Sans SC</translation>
    </message>
    <message>
      <source>WenQuanYi Micro Hei</source>
      <translation>WenQuanYi Micro Hei</translation>
    </message>
    <message>
      <source>redrawn after every step</source>
      <translation>每一步后重绘</translation>
    </message>
    <message>
      <source>Clear markers</source>
      <translation>清除标记</translation>
    </message>
    <message>
      <source>Clear profile</source>
      <translation>清除剖面</translation>
    </message>
    <message>
      <source>Export PNG</source>
      <translation>导出 PNG</translation>
    </message>
    <message>
      <source>Tables (*.csv *.txt *.xlsx *.xls);;All files (*)</source>
      <translation>表格 (*.csv *.txt *.xlsx *.xls);;所有文件 (*)</translation>
    </message>
    <message>
      <source>Logs (*.las *.csv *.txt *.xlsx *.xls);;LAS (*.las);;Tables (*.csv *.txt *.xlsx *.xls)</source>
      <translation>测井曲线 (*.las *.csv *.txt *.xlsx *.xls);;LAS (*.las);;表格 (*.csv *.txt *.xlsx *.xls)</translation>
    </message>
    <message>
      <source>No boreholes loaded.</source>
      <translation>未载入钻孔。</translation>
    </message>
    <message>
      <source>log interval</source>
      <translation>对数间隔</translation>
    </message>
    <message>
      <source>water level</source>
      <translation>水位</translation>
    </message>
    <message>
      <source>geophysical log</source>
      <translation>地球物理测井曲线</translation>
    </message>
    <message>
      <source>Easting</source>
      <translation>东坐标</translation>
    </message>
    <message>
      <source>Northing</source>
      <translation>北坐标</translation>
    </message>
    <message>
      <source>Ground (m)</source>
      <translation>地面 (m)</translation>
    </message>
    <message>
      <source>Datum offset (m)</source>
      <translation>基准面偏移 (m)</translation>
    </message>
    <message>
      <source>Top (m)</source>
      <translation>顶 (m)</translation>
    </message>
    <message>
      <source>Bottom (m)</source>
      <translation>底部（m）</translation>
    </message>
    <message>
      <source>Unit</source>
      <translation>单位</translation>
    </message>
    <message>
      <source>Description</source>
      <translation>描述</translation>
    </message>
    <message>
      <source>Depth (m)</source>
      <translation>深度 (m)</translation>
    </message>
    <message>
      <source>Head (m)</source>
      <translation>水头 (m)</translation>
    </message>
    <message>
      <source>Curve</source>
      <translation>曲线</translation>
    </message>
    <message>
      <source>Depths (m)</source>
      <translation>深度 (m)</translation>
    </message>
    <message>
      <source>Colour</source>
      <translation>颜色</translation>
    </message>
    <message>
      <source>Label</source>
      <translation>标签</translation>
    </message>
    <message>
      <source>Well locations: well_id, easting, northing, ground_elevation, crs, datum_offset, source (CSV or XLSX).</source>
      <translation>钻孔位置：well_id、easting、northing、ground_elevation、crs、datum_offset、source（CSV 或 XLSX）。</translation>
    </message>
    <message>
      <source>Lithology intervals: well_id, top, bottom, unit, description, length_unit (m or ft).</source>
      <translation>岩性层段：well_id、top、bottom、unit、description、length_unit（m 或 ft）。</translation>
    </message>
    <message>
      <source>Water levels…</source>
      <translation>水位…</translation>
    </message>
    <message>
      <source>Water levels: well_id, datetime, and depth_below_ground or head_elevation; optional reference, reference_height, length_unit.</source>
      <translation>水位：well_id、datetime，以及 depth_below_ground 或 head_elevation；可选 reference、reference_height、length_unit。</translation>
    </message>
    <message>
      <source>Geophysical logs…</source>
      <translation>地球物理测井曲线…</translation>
    </message>
    <message>
      <source>Borehole geophysics - gamma, conductivity, resistivity, temperature ... - as a LAS 2.0 file, or a table of well_id, depth and one column per curve ('gamma [API]').</source>
      <translation>钻孔地球物理——自然伽马、电导率、电阻率、温度等——LAS 2.0 文件，或包含 well_id、深度及每条曲线一列（'gamma [API]'）的表格。</translation>
    </message>
    <message>
      <source>Lower</source>
      <translation>下限</translation>
    </message>
    <message>
      <source>Upper</source>
      <translation>上限</translation>
    </message>
    <message>
      <source>gather blue–white–red</source>
      <translation>道集 蓝–白–红</translation>
    </message>
    <message>
      <source>Sequential</source>
      <translation>顺序</translation>
    </message>
    <message>
      <source>Diverging</source>
      <translation>发散型</translation>
    </message>
    <message>
      <source>Export CSV</source>
      <translation>导出 CSV</translation>
    </message>
    <message>
      <source>Moment</source>
      <translation>磁矩</translation>
    </message>
    <message>
      <source>Gate</source>
      <translation>时窗</translation>
    </message>
    <message>
      <source>Centre (us)</source>
      <translation>中心 (us)</translation>
    </message>
    <message>
      <source>Open (us)</source>
      <translation>开启 (us)</translation>
    </message>
    <message>
      <source>Close (us)</source>
      <translation>终止 (us)</translation>
    </message>
    <message>
      <source>Value (V)</source>
      <translation>值 (V)</translation>
    </message>
    <message>
      <source>Rel. std</source>
      <translation>相对标准差</translation>
    </message>
    <message>
      <source>Flag</source>
      <translation>标记</translation>
    </message>
    <message>
      <source>Verdict</source>
      <translation>结论</translation>
    </message>
    <message>
      <source>Layer cells</source>
      <translation>层单元</translation>
    </message>
    <message>
      <source>Station</source>
      <translation>测点</translation>
    </message>
    <message>
      <source>Elev (m)</source>
      <translation>高程 (m)</translation>
    </message>
    <message>
      <source>Tx-Rx (m)</source>
      <translation>收发距 (m)</translation>
    </message>
    <message>
      <source>LM kept</source>
      <translation>LM 保留</translation>
    </message>
    <message>
      <source>LM held</source>
      <translation>LM 固定</translation>
    </message>
    <message>
      <source>LM std</source>
      <translation>LM 标准差</translation>
    </message>
    <message>
      <source>HM kept</source>
      <translation>HM 保留</translation>
    </message>
    <message>
      <source>HM held</source>
      <translation>HM 保持</translation>
    </message>
    <message>
      <source>HM std</source>
      <translation>HM 标准差</translation>
    </message>
    <message>
      <source>Gates</source>
      <translation>时窗</translation>
    </message>
    <message>
      <source>Gates kept</source>
      <translation>保留时窗</translation>
    </message>
    <message>
      <source>Tx-Rx distance</source>
      <translation>收发距</translation>
    </message>
    <message>
      <source>LM gates kept</source>
      <translation>保留的 LM 时窗</translation>
    </message>
    <message>
      <source>HM gates kept</source>
      <translation>保留的 HM 时窗</translation>
    </message>
    <message>
      <source>Instrument and geometry</source>
      <translation>仪器与几何</translation>
    </message>
    <message>
      <source>System (as modelled)</source>
      <translation>系统（按模拟）</translation>
    </message>
    <message>
      <source>Acquisition protocol</source>
      <translation>采集协议</translation>
    </message>
    <message>
      <source>Inversion settings in the file</source>
      <translation>文件中的反演设置</translation>
    </message>
    <message>
      <source>Recovered 3D model</source>
      <translation>反演得到的三维模型</translation>
    </message>
    <message>
      <source> The smoothness stops at the zone outlines, so the model may jump there.</source>
      <translation> 光滑约束在分区边界处中断，因此模型在该处可能出现跳变。</translation>
    </message>
    <message>
      <source>Inversion mesh</source>
      <translation>反演网格</translation>
    </message>
    <message>
      <source>The ADTLERT time-lapse backend does not take zones: they will not be applied. Use the in-house engine to invert with them.</source>
      <translation>ADTLERT 时移后端不接受分区：分区将不会生效。如需使用分区进行反演，请使用内置引擎。</translation>
    </message>
    <message>
      <source>The ADTLERT time-lapse backend does not take zone values: they set neither its start nor its reference model, but the smoothness still stops at the zone outlines. Use the in-house engine to invert with the values.</source>
      <translation>ADTLERT 时移后端不接受分区取值：它们既不设定初始模型也不设定参考模型，但光滑约束仍在分区边界处断开。如需使用这些取值进行反演，请使用内置引擎。</translation>
    </message>
    <message>
      <source>Rebuild the mesh so its cell edges run along the outlines; it is rebuilt after every zone edit.</source>
      <translation>重建网格，使其单元边沿轮廓线分布；每次编辑分区后都会重建。</translation>
    </message>
    <message>
      <source>No smoothing across the outlines: the model may jump there. Cut edges are drawn in black.</source>
      <translation>不跨轮廓线进行光滑：模型在该处可能出现突变。切断的边以黑色绘制。</translation>
    </message>
    <message>
      <source>Velocity (m/s)</source>
      <translation>速度 (m/s)</translation>
    </message>
    <message>
      <source>contour values</source>
      <translation>等值线数值</translation>
    </message>
    <message>
      <source>fine values</source>
      <translation>精细值</translation>
    </message>
    <message>
      <source>Change from baseline (%)</source>
      <translation>相对基准的变化 (%)</translation>
    </message>
    <message>
      <source>contour grid</source>
      <translation>等值线网格</translation>
    </message>
    <message>
      <source>fine mesh</source>
      <translation>精细网格</translation>
    </message>
    <message>
      <source>fine mask</source>
      <translation>精细遮罩</translation>
    </message>
    <message>
      <source>contour mask</source>
      <translation>等值线遮罩</translation>
    </message>
    <message>
      <source>A folder with this name is already there and is not empty. Choose another name.</source>
      <translation>已存在同名且非空的文件夹。请另选名称。</translation>
    </message>
    <message>
      <source>Type a name for the project.</source>
      <translation>请输入工程名称。</translation>
    </message>
    <message>
      <source>A project name cannot contain control characters.</source>
      <translation>工程名称不能包含控制字符。</translation>
    </message>
    <message>
      <source>A project name cannot end with a full stop.</source>
      <translation>工程名称不能以句点结尾。</translation>
    </message>
    <message>
      <source>Use a name of 100 characters or fewer.</source>
      <translation>名称不得超过 100 个字符。</translation>
    </message>
    <message>
      <source>A file with this name is already there. Choose another name.</source>
      <translation>已存在同名文件。请另选名称。</translation>
    </message>
    <message>
      <source>A project with this name is already there. Choose another name, or use Open Project.</source>
      <translation>已存在同名工程。请另选名称，或使用“打开工程”。</translation>
    </message>
    <message>
      <source>Choose where to keep the project.</source>
      <translation>选择工程的保存位置。</translation>
    </message>
    <message>
      <source>Choose a full folder path for the location, or use Browse…</source>
      <translation>请为位置选择完整的文件夹路径，或使用“浏览…”</translation>
    </message>
    <message>
      <source>Restore</source>
      <translation>恢复</translation>
    </message>
    <message>
      <source>Action</source>
      <translation>操作</translation>
    </message>
    <message>
      <source>Items</source>
      <translation>项数</translation>
    </message>
    <message>
      <source>Reason</source>
      <translation>原因</translation>
    </message>
    <message>
      <source>Criterion</source>
      <translation>判据</translation>
    </message>
    <message>
      <source>high misfit — check data errors / λ / geometry</source>
      <translation>拟合差较大——请检查数据误差 / λ / 几何</translation>
    </message>
    <message>
      <source>effective-error misfit (error-calibrated, not a raw-fit verdict)</source>
      <translation>有效误差拟合差（经误差校准，并非原始拟合结论）</translation>
    </message>
    <message>
      <source>no chi-square reported</source>
      <translation>未报告卡方值</translation>
    </message>
    <message>
      <source>excellent fit (χ² ≈ 1)</source>
      <translation>拟合极好（χ² ≈ 1）</translation>
    </message>
    <message>
      <source>good fit</source>
      <translation>拟合良好</translation>
    </message>
    <message>
      <source>fair fit — consider tuning λ or errors</source>
      <translation>拟合一般——可考虑调整 λ 或误差</translation>
    </message>
    <message>
      <source>Final</source>
      <translation>最终</translation>
    </message>
    <message>
      <source>Final χ²</source>
      <translation>最终 χ²</translation>
    </message>
    <message>
      <source>Which reciprocal pairs the error model is fitted to.

All pairs (before filtering): every pair, as read.
Pairs kept by the filter: only the pairs whose readings pass the Data QC checks applied with Apply filter. The reciprocal-error limit under More checks is the check that removes outlier pairs. The pairs left out are drawn in grey.

This choice holds wherever the model is fitted: the data errors when they are taken from the reciprocal error model, the QC report, the settings file and the run's figure.</source>
      <translation>误差模型所拟合的互易对。

所有数据对（过滤前）：读入的全部数据对。
过滤后保留的数据对：仅包含读数通过“应用过滤”所执行的数据 QC 检查的数据对。“更多检查”下的互易误差限值是剔除离群数据对的检查项。未纳入的数据对以灰色绘制。

此选择在所有拟合该模型的地方均生效：取自互易误差模型的数据误差、QC 报告、设置文件以及运行生成的图件。</translation>
    </message>
    <message>
      <source>All pairs (before filtering)</source>
      <translation>所有数据对（滤除前）</translation>
    </message>
    <message>
      <source>Pairs kept by the filter</source>
      <translation>滤波保留的配对</translation>
    </message>
    <message>
      <source>No pairs to fit yet.</source>
      <translation>尚无可拟合的数据对。</translation>
    </message>
    <message>
      <source>Too few pairs for a model: at least 15 are needed.</source>
      <translation>数据对太少，无法建立模型：至少需要 15 对。</translation>
    </message>
    <message>
      <source>Set the traces, clean-up and velocity on the right, then press &lt;b&gt;Stack the line&lt;/b&gt;.&lt;br&gt;The stacked section appears here.</source>
      <translation>在右侧设置道、清理和速度，然后点击&lt;b&gt;叠加测线&lt;/b&gt;。&lt;br&gt;叠加剖面将显示在此处。</translation>
    </message>
    <message>
      <source>Stacked section</source>
      <translation>叠加断面</translation>
    </message>
    <message>
      <source>Velocity check</source>
      <translation>速度检查</translation>
    </message>
    <message>
      <source>Flat-event check</source>
      <translation>水平同相轴检查</translation>
    </message>
    <message>
      <source>Amplitude image</source>
      <translation>振幅图像</translation>
    </message>
    <message>
      <source>Wiggle</source>
      <translation>波形</translation>
    </message>
    <message>
      <source>Image + wiggle</source>
      <translation>图像 + 波形</translation>
    </message>
    <message>
      <source>Z elevation</source>
      <translation>Z 高程</translation>
    </message>
    <message>
      <source>Traditional wiggle</source>
      <translation>传统波形</translation>
    </message>
    <message>
      <source>Apparent resistivity (ohm.m)</source>
      <translation>视电阻率 (Ω·m)</translation>
    </message>
    <message>
      <source>Chargeability (%)</source>
      <translation>视极化率 (%)</translation>
    </message>
    <message>
      <source>Geometric factor (m)</source>
      <translation>装置系数 (m)</translation>
    </message>
    <message>
      <source>Rejected (1) or kept (0)</source>
      <translation>已剔除 (1) / 保留 (0)</translation>
    </message>
    <message>
      <source>Error (%)</source>
      <translation>误差 (%)</translation>
    </message>
    <message>
      <source>Line peak (dB)</source>
      <translation>工频峰值 (dB)</translation>
    </message>
    <message>
      <source>Noise RMS</source>
      <translation>噪声均方根</translation>
    </message>
    <message>
      <source>SNR (dB)</source>
      <translation>信噪比 (dB)</translation>
    </message>
    <message>
      <source>Elevation (m)</source>
      <translation>高程 (m)</translation>
    </message>
    <message>
      <source>Current (A)</source>
      <translation>电流 (A)</translation>
    </message>
    <message>
      <source>Primary voltage Vp</source>
      <translation>一次场电压 Vp</translation>
    </message>
    <message>
      <source>Current electrode A</source>
      <translation>供电电极 A</translation>
    </message>
    <message>
      <source>Current electrode B</source>
      <translation>供电电极 B</translation>
    </message>
    <message>
      <source>Potential electrode M</source>
      <translation>测量电极 M</translation>
    </message>
    <message>
      <source>Potential electrode N</source>
      <translation>测量电极 N</translation>
    </message>
    <message>
      <source>Electrode</source>
      <translation>电极</translation>
    </message>
    <message>
      <source>Transmitter</source>
      <translation>发射</translation>
    </message>
    <message>
      <source>Receiver</source>
      <translation>接收</translation>
    </message>
    <message>
      <source>Pseudo-depth: |AM|/2 (pole-dipole), |AB-MN midpoints|/2 (B on the line)</source>
      <translation>拟深度：三极装置取 |AM|/2；B 在测线上时取 AB 与 MN 中点距离的一半</translation>
    </message>
    <message>
      <source>Pseudo-depth: 0.19 x electrode spread (Edwards 1977)</source>
      <translation>拟深度：电极跨度的 0.19 倍（Edwards 1977）</translation>
    </message>
    <message>
      <source>Channel</source>
      <translation>通道</translation>
    </message>
    <message>
      <source>Floor</source>
      <translation>噪声底</translation>
    </message>
    <message>
      <source>Whole record</source>
      <translation>全段</translation>
    </message>
    <message>
      <source>On-time (steady)</source>
      <translation>供电段（平稳）</translation>
    </message>
    <message>
      <source>End of on-time</source>
      <translation>供电段末</translation>
    </message>
    <message>
      <source>Late off-time</source>
      <translation>断电段后段</translation>
    </message>
    <message>
      <source>First minute</source>
      <translation>第一分钟</translation>
    </message>
    <message>
      <source>Last minute</source>
      <translation>最后一分钟</translation>
    </message>
    <message>
      <source>Current and potential pairs</source>
      <translation>供电与测量电极对</translation>
    </message>
    <message>
      <source>Pseudo-depth points</source>
      <translation>拟深度点</translation>
    </message>
    <message>
      <source>Labels</source>
      <translation>标签</translation>
    </message>
    <message>
      <source>Top</source>
      <translation>俯视</translation>
    </message>
    <message>
      <source>Along the line</source>
      <translation>沿测线</translation>
    </message>
    <message>
      <source>Across the line</source>
      <translation>垂直测线</translation>
    </message>
    <message>
      <source>Oblique</source>
      <translation>斜视</translation>
    </message>
    <message>
      <source>Rows of date, depth and temperature, or one column per sensor depth. Without a date column the profile is held constant in time.</source>
      <translation>每行为日期、深度和温度，或每个传感器深度占一列。若无日期列，则该剖面在时间上保持不变。</translation>
    </message>
    <message>
      <source>Rows of date (or day) and the surface temperature.</source>
      <translation>每行为日期（或天数）和地表温度。</translation>
    </message>
    <message>
      <source>Choose the measured temperature table: date, depth and temperature per row, or one column per sensor.</source>
      <translation>选择实测温度表：每行包含日期、深度和温度，或每个传感器一列。</translation>
    </message>
    <message>
      <source>The profile is logged against dates but the surveys are not, so the two cannot be lined up in time. Name the survey files with their acquisition date, or log the profile in days on the same clock as the surveys.</source>
      <translation>剖面按日期记录，而测量数据没有日期，因此两者无法在时间上对齐。请用采集日期命名测量文件，或按与测量相同的时钟以天为单位记录剖面。</translation>
    </message>
    <message>
      <source>Choose a CSV with the surface temperature record: a date (or a number of days) and a temperature per row.</source>
      <translation>选择包含地表温度记录的 CSV：每行一个日期（或天数）和一个温度。</translation>
    </message>
    <message>
      <source>The surface record is dated but the surveys are not, so the two cannot be lined up in time. Name the survey files with their acquisition date, or give the surface record in days on the same clock as the surveys.</source>
      <translation>地表记录带有日期，而测量数据没有，因此两者无法在时间上对齐。请用采集日期命名测量文件，或按与测量相同的时钟以天为单位给出地表记录。</translation>
    </message>
    <message>
      <source>The seasonal model needs to know where in the year each survey sits, and these surveys carry no acquisition date. Use a constant, a measured profile or a surface record in days instead.</source>
      <translation>季节模型需要知道每次测量在一年中的时间位置，而这些测量没有采集日期。请改用常数、实测剖面或以天为单位的地表记录。</translation>
    </message>
    <message>
      <source>x from</source>
      <translation>x 来源</translation>
    </message>
    <message>
      <source>Extent along x (m).</source>
      <translation>沿 x 方向的范围 (m)。</translation>
    </message>
    <message>
      <source>y from</source>
      <translation>y 来源</translation>
    </message>
    <message>
      <source>Extent along y (m).</source>
      <translation>沿 y 方向的范围 (m)。</translation>
    </message>
    <message>
      <source>z from</source>
      <translation>z 来源</translation>
    </message>
    <message>
      <source>Elevation of the bottom and of the top (m). A top at or above the ground takes the zone up to the ground.</source>
      <translation>底部和顶部高程 (m)。顶部位于地面或地面以上时，分区延伸至地面。</translation>
    </message>
    <message>
      <source>Cell faces along every zone face; generate the mesh again after moving a zone.</source>
      <translation>每个分区面均由单元面构成；移动分区后需重新生成网格。</translation>
    </message>
    <message>
      <source>Each zone a region of its own, so an inversion does not smooth across its faces.</source>
      <translation>每个分区为独立区域，因此反演不会跨分区面进行平滑。</translation>
    </message>
    <message>
      <source>During handling of the above exception, another exception occurred:</source>
      <translation>在处理上述异常期间，又发生了另一个异常：</translation>
    </message>
    <message>
      <source>The above exception was the direct cause of the following exception:</source>
      <translation>上述异常是以下异常的直接原因：</translation>
    </message>
    <message>
      <source>close other programs to free memory, or use a coarser mesh or fewer cells, and run again</source>
      <translation>关闭其他程序以释放内存，或使用更粗的网格或更少的单元，然后重新运行</translation>
    </message>
    <message>
      <source>The data have fewer than two electrodes - check the Instrument / format setting</source>
      <translation>数据中的电极少于两个，请检查“仪器 / 格式”设置</translation>
    </message>
    <message>
      <source>The disk is full - free some space and run again</source>
      <translation>磁盘已满，请释放空间后重新运行</translation>
    </message>
    <message>
      <source>A file could not be opened or written - it may be open in another program, or the folder may be read-only</source>
      <translation>无法打开或写入文件——可能已被其他程序打开，或文件夹为只读</translation>
    </message>
  </context>
  <context>
    <name>i18n</name>
    <message>
      <source>Agentic AI  /  {agent.domain}</source>
      <translation>智能体 AI  /  {agent.domain}</translation>
    </message>
    <message>
      <source> · </source>
      <translation> · </translation>
    </message>
    <message>
      <source>&lt;br&gt;</source>
      <translation>&lt;br&gt;</translation>
    </message>
    <message>
      <source>
</source>
      <translation>
</translation>
    </message>
    <message>
      <source>Refresh</source>
      <translation>刷新</translation>
    </message>
    <message>
      <source>, </source>
      <translation>, </translation>
    </message>
    <message>
      <source>

</source>
      <translation>

</translation>
    </message>
    <message>
      <source> </source>
      <translation> </translation>
    </message>
  </context>
</TS>