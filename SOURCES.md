# SOURCES — QUADC5

Каждое внешнее число и каждое утверждение о содержании чужой работы в этом проекте
появляется здесь со ссылкой, датой обращения и **дословной цитатой из выгрузки,
лежащей в `sources/`**. Ничего здесь не воспроизведено по памяти. Где текстовый слой
PDF ломает глифы, ломка оставлена видимой, а чтение помечено. Основной источник цитат —
LaTeX-исходник статьи с arXiv (`sources/eprint_2605.12828/paper.tex`), потому что он
даёт списки рёбер и коды графов без искажений слоя PDF.

Все обращения: **2026-08-19**, `curl`/`git clone`, выгрузки в `sources/`.

---

## S1 — arXiv:2605.12828 (статья, на которой стоит калибровка 0.a)

U. Tamer, Ö. E. Müstecaplıoğlu, A. Dizdar, Z. Gedik,
*The Quad-C₅ Graph: Maximum Contextuality Gap on Eight Vertices*.
https://arxiv.org/abs/2605.12828 — обращение 2026-08-19.

История подачи со страницы abs (`sources/arxiv_2605.12828_abs.html`):

> Submission history From: Ugur Tamer [ view email ]
> [v1] Tue, 12 May 2026 23:50:25 UTC (16 KB)
> [v2] Sun, 31 May 2026 16:33:09 UTC (24 KB)

Выгружена **v2** (то, что arXiv отдаёт по умолчанию на дату обращения). Датировка на
первой странице PDF: «(Dated: June 2, 2026)» — на два дня позже подачи v2; расхождение
записано, но ни на что не влияет.

Выгрузки: `sources/arxiv_2605.12828.pdf` (13 страниц), `sources/arxiv_2605.12828.pdftxt`
(извлечение pypdf, содержит 7 нулевых байт), `sources/arxiv_2605.12828.txt` (то же без
нулевых байт, 1282 строки), `sources/arxiv_2605.12828_abs.html`,
`sources/eprint_2605.12828/paper.tex` (LaTeX-исходник, 1655 строк).

### S1.1 — определение зазора (несущее определение всего проекта)

`paper.tex` строки 140–145:

> The contextuality gap
> `\begin{equation} \De(G) = \vt(G) - \al(G) \label{eq:gap_intro} \end{equation}`
> measures the separation between quantum and noncontextual descriptions within

где макросы, `paper.tex` строки 20–22: `\newcommand{\vt}{\vartheta}`,
`\newcommand{\al}{\alpha}`, `\newcommand{\De}{\Delta}`.

Контекст — неравенство CSW, `paper.tex` строки 134–139:

> `\begin{equation} \al(G) \leq \sum_{i\in V}p_i \leq \vt(G), \end{equation}`
> where `$\al(G)$` is the independence number, giving the noncontextual bound,
> and `$\vt(G)$` is the Lov\'{a}sz theta number, giving the
> projective quantum bound

Отсюда: ϑ считается для **того же** графа G, для которого считается α, рёбра G — это
отношения исключительности, и ϑ ≥ α. Знак зазора неотрицателен по построению.

### S1.2 — SDP, который надо реализовать

`paper.tex` строки 224–232:

> For a graph `$G$` on `$n$` vertices with edge set `$E$`, the Lov\'{a}sz theta
> function is given by the semidefinite program
> `\begin{equation} \vt(G) = \max_{\substack{X\succeq 0,\;\Tr(X)=1\\ X_{ij}=0\;\forall(i,j)\in E}}\; \mathbf{1}^\top X\,\mathbf{1}, \label{eq:sdp} \end{equation}`
> over the cone of `$n\times n$` positive semidefinite matrices.

и строки 242–245:

> The Lov\'{a}sz sandwich theorem gives `$\al(G)\leq\vt(G)\leq\chi(\bar{G})$`.
> The relaxation over real vectors is tight: `$\vt(G)$` equals the maximum
> in Eq.~\eqref{eq:orth_rep} even when restricted to `$|v_i\rangle\in\mathbb{R}^d$`.

### S1.3 — определение минимальной размерности d\*

`paper.tex` строки 249–260:

> `\begin{equation} \eta_d(G) = \max_{\substack{\{|v_i\rangle\}\subset\mathbb{R}^d,\; \|v_i\|=1,\\\langle v_i|v_j\rangle=0\;\forall(i,j)\in E}} \lmax\!\!\left(\sum_{i=1}^n |v_i\rangle\!\langle v_i|\right), \end{equation}`
> with `$\eta_d(G)\nearrow\vt(G)$` as `$d\to n$`.
> The minimum dimension `$d^*$` is
> `\begin{equation} d^*(G) = \min\{d : \eta_d(G)>\al(G)\}. \end{equation}`

**Читается так:** d\* определён через строгое превышение α, а не через достижение ϑ.
Это невыпуклая задача (см. S1.9 — сами авторы называют полученные d\*=4 «numerically
indicated»). Для брифа 0.d «минимальная размерность, в которой реализуется оптимальное
ортогональное представление» — это d\* в этом смысле.

### S1.4 — опорные значения n=5 и n=7

`paper.tex` строки 410–422:

> For `$n=5$`, the maximum contextuality gap is achieved by the five-cycle `$C_5$`
> (the KCBS exclusion graph):
> `\begin{equation} \al(C_5)=2,\quad\vt(C_5)=\sqrt{5},\quad\De(C_5)=\sqrt{5}-2\approx0.236. \end{equation}`
> For `$n=7$`, the maximum is the seven-cycle `$C_7$`, which
> we verify by exhaustive SDP search over all 853 connected non-isomorphic
> `$n=7$` graphs using the same pipeline:
> `\begin{equation} \vt(C_7)=\frac{7\cos(\pi/7)}{1+\cos(\pi/7)}\approx3.318,\quad \De(C_7)\approx0.318. \end{equation}`
> Both `$C_5$` and `$C_7$` are qutrit witnesses (`$d^*=3$`).

Таблица иерархии, `paper.tex` строки 1326–1341 (`\label{tab:hierarchy}`), даёт те же
значения с пятью знаками:

> `$C_5$` (KCBS) & 5 & 2 & 2.23607 & 0.23607 & 3
> `$C_7$`        & 7 & 3 & 3.31767 & 0.31767 & 3
> Wagner `$W$`   & 8 & 3 & 3.41421 & 0.41421 & 4`$^\dagger$`
> **Quad-C₅**    & 8 & 3 & 3.46784 & **0.46784** & 3
> `\noindent $^\dagger$ Numerically indicated.`

### S1.5 — топ-10 на n=8

`paper.tex` строки 445–461 (`\label{tab:n8_top10}`), колонки Rank / Note / |E| / α / ϑ / Δ / ϑ/α:

> 1  & \QC\ (`$n{=}8$` gap max)        & 10 & 3 & 3.46784 & 0.46784 & 1.15595
> 2  &                              & 11 & 3 & 3.43845 & 0.43845 & 1.14615
> 3  & Wagner `$W$`                   & 12 & 3 & 3.41421 & 0.41421 & 1.13807
> 4  &                              & 11 & 3 & 3.37228 & 0.37228 & 1.12409
> 5  &                              & 12 & 3 & 3.37228 & 0.37228 & 1.12409
> 6  &                              & 10 & 3 & 3.37228 & 0.37228 & 1.12409
> 7  & `$\dagger$` CHSH-type graph     & 16 & 2 & 2.34315 & 0.34315 & 1.17157
> 8  &                              & 11 & 3 & 3.33804 & 0.33804 & 1.11268
> 9  &                              & 17 & 2 & 2.33804 & 0.33804 & 1.16902
> 10 &                              & 18 & 2 & 2.33333 & 0.33333 & 1.16667

и текст, строки 428–430:

> \QC\ achieves `$\De=0.46784$`, exceeding the Wagner graph `$W$`
> (Rank~3) by `$0.46784-0.41421=0.05363$`, while using only 10 edges compared
> to `$W$`'s 12.

**Ранги 4, 5 и 6 вырождены по Δ** (все три 0.37228) — значит «второй-третий по списку»
из брифа проверяемы, а вот ранги 4–6 упорядочены не зазором, и совпадение порядка на
них требовать нельзя. Записано до счёта.

### S1.6 — канонический код графа-победителя и его список рёбер

`paper.tex` строки 466–476:

> The graph6 canonical encoding of this graph is
> `\verb|GCQb`o|`, which we retain as a reproducibility identifier.
> \QC\ has vertex set `$V=\{0,1,\ldots,7\}$` and edge set
> `\begin{align} E = \{&(0,3),(0,5),(1,4),(1,6),(2,5),(2,6),\nonumber\\ &(2,7),(3,6),(3,7),(4,7)\}. \end{align}`
> Its degree sequence is `$(2,2,2,2,3,3,3,3)$`: vertices `$\{0,1,4,5\}$` have
> degree~2 (``leaf'' nodes) and vertices `$\{2,3,6,7\}$` have degree~3
> (``hub'' nodes).

**Шестой символ кода — обратный апостроф `` ` `` (ASCII 96), а не апостроф `'`
(ASCII 39).** В графе6 допустимы только символы 63…126, так что `'` был бы
невалиден. Код: `` GCQb`o ``. В брифе он записан как `GCQb'o` — это опечатка
транслитерации, зафиксирована здесь и в `REPORT.md` §отклонения.

Тот же код в данных авторов, `sources/quadc5_authors_repo/all_n8_results.csv` строка 2:

> `1,GCQb`o,3,3.46784373,0.46784373,10,1.1102230246251565e-16,optimal`

### S1.7 — структура из перекрывающихся пятиугольников (предмет 0.d)

`paper.tex` строки 544–547:

> A defining structural feature is that \QC\ contains exactly four
> induced five-cycles (KCBS pentagons), listed in Table~\ref{tab:c5_subgraphs}.
> Crucially, \emph{every} one of the 10 edges belongs to exactly two of the
> four `$C_5$` subgraphs---a perfect two-fold edge coverage.

Таблица `\label{tab:c5_subgraphs}`, `paper.tex` строки 1243–1256:

> `$C_5^{(1)}$` & `$\{0,2,3,5,6\}$` & `$(0,3),(0,5),(2,5),(2,6),(3,6)$`
> `$C_5^{(2)}$` & `$\{0,2,3,5,7\}$` & `$(0,3),(0,5),(2,5),(2,7),(3,7)$`
> `$C_5^{(3)}$` & `$\{1,2,4,6,7\}$` & `$(1,4),(1,6),(2,6),(2,7),(4,7)$`
> `$C_5^{(4)}$` & `$\{1,3,4,6,7\}$` & `$(1,4),(1,6),(3,6),(3,7),(4,7)$`

и структурное описание, `paper.tex` строки 477–482:

> The graph is neither regular nor vertex-transitive.
> The four hub nodes `$\{2,3,6,7\}$` form a complete bipartite subgraph
> `$K_{2,2}$` (bipartition `$\{2,3\}\times\{6,7\}$`), while the leaf nodes
> attach as two pendant paths `$3{-}0{-}5{-}2$` and `$6{-}1{-}4{-}7$`,
> each bridging one hub pair through two degree-2 vertices.

**Это операционализируемо:** «четыре индуцированных C₅» + «каждое ребро ровно в двух
из них». Обе величины считаются и переносятся на n=9 без доопределений.

### S1.8 — наблюдение «оптимум разреженнее эталона» (предмет 0.d)

`paper.tex` строки 649–660:

> The main surprise is that \QC\ achieves a larger contextuality
> gap than `$W$` with \emph{two fewer edges}.
> Adding an edge to an exclusion graph imposes an additional orthogonality
> constraint in Eq.~\eqref{eq:sdp}, generically reducing `$\vt(G)$` while
> leaving `$\al(G)$` unchanged or reducing it.
> Naively, fewer edges should correlate with a smaller gap.
> The fact that the optimal graph is sparser than the previously leading example points
> to a more efficient contextuality geometry: the four interlocking KCBS
> pentagons in \QC\ encode more quantum advantage per edge than
> the symmetric 3-regular structure of `$W$`.

**Точная формулировка наблюдения:** оно сделано на одном сравнении (Quad-C₅ 10 рёбер
против Вагнера 12), а не как тренд по всему списку. В топ-10 из S1.5 числа рёбер идут
10, 11, 12, 11, 12, 10, 16, 11, 17, 18 — монотонности нет. Перенос «оптимум разреженнее»
в тренд «|E| против ранга» — это уже наша конструкция, и она так и помечается.

### S1.9 — что в статье получено численно, а не доказано (границы калибровки)

`paper.tex` строки 310–330 (метод SDP):

> We solve Eq.~\eqref{eq:sdp} using CVXPY with the
> SCS solver for bulk screening of all 11{,}117
> connected graphs; SCS provides typical precision of `$10^{-4}$--$10^{-6}$`,
> sufficient for ranking.
> The top 50 candidates were re-solved with the CLARABEL solver
> (precision `$\sim\!10^{-10}$--$10^{-12}$`), whose values are reported
> in all tables.
> For every graph in the top 50, the SCS--CLARABEL discrepancy is
> `$|\vt_\text{SCS}-\vt_\text{CLARABEL}|<10^{-7}$` and the CLARABEL primal
> feasibility residual satisfies `$r_p<4\times10^{-10}$`, providing
> numerical evidence against artefacts.
> The bulk scan completed in under four minutes on a standard laptop CPU.

`paper.tex` строки 574–586 (оговорка про d\*):

> We note that the claim `$\eta_3(W)=\al=3$` is a \emph{lower-bound} result:
> the optimization confirms that the best 3D representation found attains
> `$\lmax=\al$`, but without an SDP upper-bound verification one cannot rule out
> a 3D configuration with `$\lmax>3$` that the heuristic failed to find.
> [...] a formal `$d^*=4$` proof remains an open question.

`paper.tex` строки 630–634 (про замкнутую форму ϑ):

> By contrast, the candidate polynomial for `$\vt(\QC)$`
> at 15-digit precision has `$r\approx20\gg1$` and is a false positive.
> A reliable closed form for `$\vt$` requires a high-precision solver such as
> SDPA-GMP at `$\geq30$` significant digits.

**Следствие для нас:** замкнутой формы ϑ(Quad-C₅) в статье нет; сверяться можно только
с числом 3.46784. Значения d\*=4 у авторов — нижние оценки от эвристики, не доказательства;
любой наш d\*, полученный тем же способом, наследует ту же оговорку.

### S1.10 — заявление о доступности данных

`paper.tex` строки 901–908:

> All graph data derive from the publicly available McKay database
> (`\texttt{graph8.g6}`, `\url{https://users.cecs.anu.edu.au/~bdm/data/}`).
> Complete edge lists are given in Table~\ref{tab:edgelists} (Appendix~\ref{app:tables});
> All Python scripts and data files are publicly available at
> `\url{https://github.com/ugurtamerphys/quad-c5-contextuality}` and archived on
> Zenodo~\cite{Tamer2026zenodo}.

Библиография, `paper.tex` строки 1647–1651:

> `\bibitem{Tamer2026zenodo}` U.~Tamer, ... \emph{Quad-C5 contextuality: code and data},
> Zenodo (2026), `\doi{10.5281/zenodo.20465134}`.

### S1.11 — списки рёбер топ-6 (нужны для сверки рангов 2–6)

`paper.tex` строки 1396–1416 (`\label{tab:edgelists}`), колонки Rank / Δ / d\* / |E| / список:

> 1 & 0.46784 & 3 & 10 & `$(0,3),(0,5),(1,4),(1,6),(2,5),(2,6),(2,7),(3,6),(3,7),(4,7)$`
> 2 & 0.43845 & 3 & 11 & `$(0,3),(0,5),(1,4),(1,5),(1,7),(2,5),(2,6),(2,7),(3,6),(3,7),(4,6)$`
> 3 (Wagner `$W$`) & 0.41421 & 4`$^\dagger$` & 12 & `$(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),(0,4),(1,5),(2,6),(3,7)$`
> 4 & 0.37228 & 3 & 11 & `$(0,3),(0,5),(0,7),(1,4),(1,6),(2,5),(2,6),(2,7),(3,6),(3,7),(4,7)$`
> 5 & 0.37228 & 4`$^\dagger$` & 12 & `$(0,3),(0,5),(1,4),(1,5),(1,6),(2,5),(2,6),(2,7),(3,6),(3,7),(4,7),(5,7)$`
> 6 & 0.37228 & 3 & 10 & `$(0,3),(0,4),(0,7),(1,4),(1,5),(2,5),(2,6),(2,7),(3,6),(4,7)$`

Ранг 3 задан как цикл 0-1-…-7-0 плюс четыре главные диагонали — это лестница Мёбиуса
`$M_8$`, она же граф Вагнера `$V_8$`. Определение берётся отсюда, а не по памяти.

### S1.12 — как авторы перечисляли графы

`paper.tex` строки 286–292:

> McKay's database (`\texttt{graph8.g6}`) contains all
> 12{,}346 non-isomorphic simple graphs on `$n=8$` vertices;
> of these, 11{,}117 are connected (OEIS A001349).
> We retrieved all graphs, filtered for connectivity, and applied the
> analysis pipeline to the connected subset.
> Non-isomorphic graphs on `$n=5$` and `$n=7$` were obtained from NetworkX's
> Graph Atlas.

и строки 302–306 (α):

> For each graph `$G$` we compute `$\al(G)=\omega(\bar{G})$` via maximum-weight
> clique search on the complement, implemented in NetworkX.
> For `$n\leq8$` this is exact; we cross-validated all 11{,}117 results by
> independent brute-force enumeration of all `$2^8=256$` vertex subsets,
> finding perfect agreement across every graph.

---

## S2 — репозиторий авторов (код, который надо прогнать на своей машине)

https://github.com/ugurtamerphys/quad-c5-contextuality — обращение 2026-08-19,
`git clone --depth 50` в `sources/quadc5_authors_repo/`.

HEAD на дату обращения:

> `bfacfd098be18f84bf332547be634db059978dcb 2026-05-30 18:57:11 +0300 ugurtamerphys Read ME`

Файлы (все в корне): `certification.py` (465 строк), `noise_robustness.py` (99),
`dual_certificate.py` (97), `graph8.g6` (12346 строк), `all_n8_results.csv` (11118 строк
с заголовком), `top50_certification.csv`, `certified_intervals.csv`,
`eta3_certification.csv`, `README.md`.

### S2.1 — архив Zenodo идентичен GitHub

Zenodo record 20465134 (`sources/zenodo_20465134.json`), обращение 2026-08-19:

> `"title": "ugurtamerphys/quad-c5-contextuality: First release"`,
> `"doi": "10.5281/zenodo.20465134"`, `"publication_date": "2026-05-30"`,
> файл `ugurtamerphys/quad-c5-contextuality-v1.0.0.zip`, 204502 байт.

Распакован в `sources/zenodo_extract/ugurtamerphys-quad-c5-contextuality-bfacfd0/`.
Побайтовое сравнение всех шести содержательных файлов (`certification.py`,
`dual_certificate.py`, `noise_robustness.py`, `all_n8_results.csv`,
`top50_certification.csv`, `graph8.g6`) с клоном GitHub: **совпадение по всем шести**.
Суффикс каталога `bfacfd0` совпадает с HEAD клона. Архив и репозиторий — одно и то же
состояние; расхождения «Zenodo против GitHub» нет.

### S2.2 — README расходится с раскладкой репозитория

`sources/quadc5_authors_repo/README.md`, таблица содержимого, называет пути
`data/all_n8_results.csv`, `data/top50_certification.csv`,
`data/certified_intervals.csv`, `data/eta3_certification.csv`:

> | `data/all_n8_results.csv` | Independence number and Lovász theta for all 11,117 connected 8-vertex graphs |

Каталога `data/` в репозитории нет — все CSV лежат в корне. Расхождение косметическое,
но записано, потому что «прогнать код авторов» упирается в такие мелочи.

### S2.3 — что именно считает `certification.py`

`sources/quadc5_authors_repo/certification.py` строки 82–95:

> ```
> def lovasz_theta_with_residuals(G, solver):
>     n = G.number_of_nodes()
>     nodes = sorted(G.nodes())
>     idx = {v: i for i, v in enumerate(nodes)}
>     X = cp.Variable((n, n), PSD=True)
>     cons = [cp.trace(X) == 1]
>     for u, v in G.edges():
>         cons += [X[idx[u], idx[v]] == 0]
>     prob = cp.Problem(cp.Maximize(cp.sum(X)), cons)
> ```

Это буквально уравнение (1) из S1.2: `cp.sum(X)` = 1ᵀX1, `PSD=True` в CVXPY влечёт
симметричность. Наша реализация обязана решать ту же задачу, но написана независимо.

Строки 29–47 — два независимых способа для α (клика в дополнении и полный перебор
подмножеств), тот же приём, что предписывает правило репозитория.

### S2.4 — опорные числа авторов из их же данных (не из статьи)

`sources/quadc5_authors_repo/all_n8_results.csv`, строки 2–5
(заголовок `rank,graph6,alpha,theta_scs,delta_scs,edges,pr_scs,status_scs`):

> `1,GCQb`o,3,3.46784373,0.46784373,10,1.1102230246251565e-16,optimal`
> `2,GCR`r_,3,3.43844718,0.43844718,11,1.7257093251300215e-14,optimal`
> `3,GCrb`o,3,3.41421356,0.41421356,12,5.687828984040464e-14,optimal`
> `4,GCRb`w,3,3.37228133,0.37228133,12,2.5138757657234343e-18,optimal`

**Расхождение статья ↔ данные, найденное до всякого счёта:** таблица S1.5 даёт рангу 4
одиннадцать рёбер (`4 & 0.37228 & 3 & 11`), а CSV — двенадцать (`...,0.37228133,12,...`).
Список рёбер ранга 4 в S1.11 содержит 11 пар, список ранга 5 — 12 пар. То есть в CSV
на четвёртом месте стоит граф, который в статье пятый, и наоборот. Полные строки CSV
(`` GCRb`w ``, `GCQbdo`, `` GCp`dO ``) дают |E| = 12, 11, 10 при Δ_CLARABEL =
0.37228136, 0.37228134, 0.37228132 — три значения совпадают в пределах 2e-8, то есть
внутри собственной погрешности солвера авторов, но не побитово. Перестановка рангов 4 и 5
между статьёй и данными есть перестановка внутри группы численно неразличимых значений,
а не противоречие в числах. Записано как факт до начала работы, как требует бриф.
Следствие для гейта: требовать совпадения порядка ниже ранга 3 нельзя, а вот **множество**
{ранг 4, ранг 5, ранг 6} проверяемо как множество.

`sources/quadc5_authors_repo/top50_certification.csv`, строка 2, даёт CLARABEL-значение
для победителя:

> `1,GCQb`o,3,3.46784373,3.46784377,0.46784373,0.46784377,10,...,optimal,optimal`

то есть ϑ_SCS = 3.46784373 и ϑ_CLARABEL = 3.46784377; разница 4.4e-8. Статья печатает
3.46784. Все три согласованы в пределах 1e-6, и допуск гейта 0.a именно этим и
обоснован (см. `PREREGISTRATION.md` §0.a).

---

## S3 — база графов Маккея (первичный вход конвейера)

https://users.cecs.anu.edu.au/~bdm/data/ — обращение 2026-08-19, `curl`.
Выгрузки: `sources/mckay_graph7c.g6`, `sources/mckay_graph8c.g6`, `sources/mckay_graph9c.g6`.

Подсчёт строк в выгрузках (`wc -l`), **проверено самостоятельно, а не принято из брифа**:

| файл | строк | что это |
|---|---:|---|
| `mckay_graph7c.g6` | 853 | связные неизоморфные простые графы на 7 вершинах |
| `mckay_graph8c.g6` | 11 117 | то же на 8 вершинах |
| `mckay_graph9c.g6` | 261 080 | то же на 9 вершинах |

Числа 853 и 11 117 совпадают с тем, что заявляет статья (S1.4, S1.12). Число 261 080
совпадает с числом из брифа; бриф требовал не принимать его на слово — оно получено
здесь из независимой выгрузки. Файл `graph8.g6` авторов (12 346 строк, все графы на 8
вершинах, не только связные) — из того же источника, что подтверждает S1.10.

---

## S4 — аналитические значения для калибровки SDP

Значения ниже используются как эталон для допуска SDP. Формула для циклов взята из S1.4
(она напечатана в статье для C₇ в общем виде через n). Значения ϑ(Cₙ) для нечётного n:

ϑ(Cₙ) = n·cos(π/n) / (1 + cos(π/n)) — `paper.tex` строка 419, записана для n=7.

Формулу для полных и пустых графов статья не печатает; она берётся из теоремы Ловаса о
сэндвиче, процитированной в S1.2: α(G) ≤ ϑ(G) ≤ χ(Ḡ). Для полного графа Kₙ имеем
α = 1 и χ(K̄ₙ) = χ(пустой) = 1, откуда ϑ(Kₙ) = 1 зажат между равными границами. Для
пустого графа Ēₙ имеем α = n и χ(Kₙ) = n, откуда ϑ = n. **Оба значения выведены здесь
из процитированного неравенства, а не взяты по памяти.**

Графы Кнезера из брифа: значение ϑ(K(n,k)) = C(n-1, k-1) в источниках этого проекта не
процитировано. Оно помечается **UNVERIFIED** и в решающих сравнениях не участвует;
вместо него калибровка SDP опирается на циклы, полные и пустые графы, где вывод есть
выше. Если понадобится — берётся частный случай C₅ = K(5,2), который уже покрыт формулой
циклов.

---

# Stage 1 — дополнение к источникам

Обращения **2026-08-19** (тот же день, что и Stage 0), выгрузки в `sources/`.

## S5 — nauty / geng (генератор для 1.a)

B. D. McKay, A. Piperno, *nauty and Traces*.
Дистрибутив: https://users.cecs.anu.edu.au/~bdm/nauty/ — обращение 2026-08-19.
Выгрузка: `sources/nauty2_9_3.tar.gz`,
SHA-256 `9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b`.
Собрано из исходников в `build/nauty2_9_3` (`./configure && make geng`), потому что
пакета в системе нет и сайт pallini.di.uniroma1.it на дату обращения недоступен
(`curl` возвращает HTTP 000).

Версия из `build/nauty2_9_3/nauty.h` строка 606:

> `#define NAUTYVERSIONID (29300+HAVE_TLS)  /* 10000*version + HAVE_TLS */`

то есть 2.9.3.

**S5.1 — что делают ключи, использованные здесь.** `./geng --help`:

> `     -c    : only write connected graphs`
> `     -u    : do not output any graphs, just generate and count them`
> `     -l    : canonically label output graphs`
> `     -P    : only generate perfect graphs`
> `     -q    : suppress auxiliary output (except from -v)`

и про распараллеливание:

> ` res/mod splitting is controlled by two parameters -X# and -x# whose default`
> ` values are displayed when splitting is used. Increasing them will make the`
> ` division into parts more even at the expense of more overhead, but you must`
> ` use the same values for all parts. Splitting obeys the laws of modular`
> ` arithmetic, for example 3/7 is the union of 3/14 and 10/14`

**Читается так, и это ловушка, записанная до счёта:** без `-l` geng выдаёт графы
в той нумерации, в какой они породились, а не в канонической. Коды graph6 тогда
законно отличаются от опубликованных `graph9c.g6`, хотя множество классов изоморфизма
то же. Гейт 1.a поэтому формулируется в двух чтениях (см. `PREREGISTRATION_STAGE1.md` §1.a).

**S5.2 — независимая проверка отсева.** Ключ `-P` («only generate perfect graphs»)
даёт распознавание совершенных графов, написанное не нами. Он используется как
внешняя сверка нашего `quadc5/perfect.py`, которого в Stage 0 не с чем было сверить.
Замечание: определение совершенства у geng мы не читали в исходниках, поэтому
совпадение счётчиков — свидетельство, а не доказательство, и так и отчитывается.

**S5.3 — тривиальная проверка работоспособности.** `./geng -c 5 -u`:

> `>Z 21 graphs generated in 0.00 sec`

21 — известное число связных графов на 5 вершинах (OEIS A001349), совпадает.

## S6 — числа, которые Stage 1 обязан подтвердить сам

Stage 0 подтвердил собственной выгрузкой 853 / 11 117 / 261 080 (S3). Число
**11 716 571** для связных графов на 10 вершинах взято из брифа Stage 1 и на момент
написания предрегистрации **не подтверждено**: оно помечается UNVERIFIED и
подтверждается или опровергается прогоном `geng -c 10 -u` в блоке 1.a. Файл
`graph10.g6` намеренно не скачивается — бриф требует генерации потоком.

---

# Stage 2 — дополнение к источникам

Обращения **2026-08-20**.

## S7 — инструменты произвольной точности

**Что выбрано и почему не SDPA-GMP.** Бриф 2.a называет SDPA-GMP как один из вариантов.
На этой машине он **недоступен без сборки цепочки зависимостей от исходников**:
системного пакета `sdpa` нет (`apt-cache policy sdpa` → `Installed: (none)`), заголовков
`/usr/include/gmp.h` и `/usr/include/mpfr.h` нет, прав root нет. Сборка SDPA-GMP
потребовала бы сначала собрать GMP и MPFR, то есть внести в проект три крупные
непроверенные зависимости ради величины, которая по условию задачи является **только
входом для поиска**, а не результатом.

Выбрано: **собственный уточнитель на mpmath 1.3.0**, стартующий с двойной точности и
доводящий решение методом Ньютона по условиям Каруша—Куна—Таккера. Обоснование
записано до прогона:

1. mpmath уже является зависимостью проекта, чистый Python, без сборки.
2. Ньютон на системе ККТ сходится квадратично: число верных знаков удваивается за
   итерацию, так что 60+ знаков достигаются за 4–5 шагов от двойной точности.
3. **Главное.** Итог стадии — точный сертификат (2.c), который проверяется в
   рациональной и алгебраической арифметике и **не зависит от того, каким солвером
   найден кандидат**. Доверие к высокоточному солверу не является несущим: он
   поставляет гипотезу, а не доказательство. Поэтому цена ошибки в нём — потерянное
   время, а не неверный результат. Ровно по этой причине тратить силы на сборку
   SDPA-GMP нецелесообразно, а калибровочный гейт 2.a всё равно обязателен.

Возможности mpmath, проверенные на игрушечных входах до запечатывания предрегистрации:
`svd_r`, `eigsy`, `qr_solve`, `lu_solve`, `cholesky`, `pslq` — все присутствуют.
PSLQ на числе Пластика 1.3247179572447460259609088544780973407344040569017333645340150503
вернул `[1, 1, 0, -1]`, то есть t³ = t + 1, и вернул `None` при попытке степени 2 —
и находит настоящее соотношение, и не выдумывает лишнего.

## S8 — точная алгебраическая арифметика

sympy 1.14.0. Используются:
- `CRootOf(p, k)` — сертифицированная изоляция вещественных корней. Проверено:
  для `x³ − x − 1` даёт изолирующий интервал с **рациональными** концами
  (тип `PythonMPQ`), то есть пригодный для строгой интервальной арифметики без
  плавающей точки.
- `QQ.algebraic_field(θ)` — арифметика в числовом поле; на проверке
  `θ² + 3/7` вычислено точно.

**Что именно берётся на веру и что нет.** От sympy берётся только изолирующий интервал
с рациональными концами. Всё остальное — сложение, умножение, обращение, определение
знака — реализовано в `quadc5/numfield.py` на дробях `fractions.Fraction`, и знак
элемента определяется **точно**: сначала проверка на ноль по вектору координат (базис
1, θ, …, θ^{d−1}), затем, если элемент ненулевой, сужение изолирующего интервала
делением пополам с точным рациональным вычислением знака минимального многочлена, пока
интервальная оценка значения не перестанет содержать ноль. Плавающая точка в этот слой
не входит вовсе.

## S9 — уже доказанные значения, на которых калибруется солвер (гейт 2.a)

Все четыре получены в стадиях 0 и 1 этого же репозитория и лежат в `results/`:

| граф | ϑ | степень поля | где доказано |
|---|---|---|---|
| C₅ (`DUW`) | √5 | 2 | `REPORT.md`, тождество 5cos(π/5)/(1+cos(π/5)) = √5 |
| C₇ (`` FCp`_ ``) | 7cos(π/7)/(1+cos(π/7)) | **3** | формула из S1.4, `paper.tex` строка 419 |
| `HCRbdO{` (n=9) | 11/3 | 1 | `runners/certify_n9_max.py`, точный примал+дуал |
| `` ICRb`yiu? `` (n=10) | 3 + √2⁄2 | 2 | `runners/certify.py`, точный примал+дуал |

C₇ — единственный из четырёх с полем степени 3, и потому он же служит проверкой всего
аппарата высших степеней: если машинерия 2.b+2.c не воспроизводит **уже известный**
кубический случай, к боевым графам она не допускается.

## S10 — повторная сверка с arXiv:2605.12828, обращение 2026-08-20

Бриф релиза предполагал, что источники брались по версии более ранней, чем v2.
**Это не так.** Проверено побайтово: `curl https://arxiv.org/e-print/2605.12828`
на 2026-08-20 отдаёт файл, идентичный выгрузке `sources/arxiv_2605.12828_eprint`,
сделанной 2026-08-19 (`cmp` без расхождений). Страница abs на обе даты перечисляет
ровно две версии, v1 и v2. То есть весь проект с самого начала цитировал v2, и
пересматривать нечего. Тем не менее четыре названных в брифе пункта перепроверены
явно, по той же выгрузке:

1. **Опорные значения** — таблица `tab:hierarchy` без изменений:
   C₅ 2.23607 / 0.23607, C₇ 3.31767 / 0.31767, Wagner 3.41421 / 0.41421,
   Quad-C₅ 3.46784 / **0.46784**.
2. **Код графа-победителя** — `paper.tex` строки 466–467, без изменений:
   > The graph6 canonical encoding of this graph is `\verb|GCQb`o|`, which we retain
   > as a reproducibility identifier.
3. **Формулировка про PSLQ** — на месте, `paper.tex` строки 634–638:
   > By contrast, the candidate polynomial for `$\vt(\QC)$` at 15-digit precision has
   > `$r\approx20\gg1$` and is a false positive.
   Именно это утверждение задавало планку Stage 2, и в v2 оно сохранено.
4. **Число рестартов** — внутреннее расхождение статьи **сохраняется в v2**:
   «300» встречается пять раз (`N=300`, `300-restart` ×2, `all 300 restarts` ×2),
   «500» — два раза (`500 independent restarts`, `All 500`). Код авторов использует
   `N_RESTARTS = 500`.

**Вывод:** ни одна наша формулировка не опирается на устаревшую версию, и ничего из
отчётов не изымается.

---

# Stage 3 — дополнение к источникам

Обращения **2026-08-20**.

## S11 — база квантовых графов (Cabello, Danielsen, López-Tarrida, Portillo)

**Адрес из брифа мёртв.** `http://www.ii.uib.no/~larsed/quantum_graphs/` на 2026-08-20
отдаёт HTTP 404 (редирект на страницу ошибки Университета Бергена). Мертвы и
`https://www.ii.uib.no/~larsed/`, и `https://www.ii.uib.no/~larsed/quantum_graphs/`,
и предполагавшееся зеркало `https://larsed.github.io/quantum_graphs/`.

**Что удалось получить.** Индексная страница базы из Wayback Machine:
- снимок `20220119160620`, выгрузка `sources/cabello_db_index.html`,
  SHA-256 в `sources/cabello_db.sha256`;
- снимок `20240420000804`, выгрузка `sources/cabello_2024.html` — содержание идентично.

Дословно со страницы (формат столбцов):

> Data format (columns): id# nauty-string α ϑ α * d upper bound for orthogonal rank
> Q=(ϑ-α)/(intersection number) S=(α * -ϑ)/(intersection number) intersection number
> intersection number of the complement graph chromatic number of the complement graph

и таблица загрузок:

> n Download Size
> 5 quantum5 1 graph
> 6 quantum6 3 graphs
> 7 quantum7 33 graphs
> 8 quantum8 498 graphs
> 9 quantum9 16533 graphs (902KB)
> 10 quantum10 975330 graphs (5.1MB compressed)

**Ключевое обстоятельство, устанавливающее объём базы:** это список **не всех** графов,
а только тех, у которых ϑ > α. Страница называет их «quantum graphs», и счётчики
(1, 3, 33, 498, 16533, 975330) — это счётчики графов с положительным зазором, а не
общее число неизоморфных графов на n вершинах.

**Сами файлы данных недостижимы.** `quantum5`…`quantum10.bz2` в Wayback Machine никогда
не сохранялись: запрос CDX по `ii.uib.no/~larsed/quantum_graphs/*` возвращает снимки
**только** индексной страницы. Поиск зеркал результата не дал. Поэтому:

- **счётчики** — проверяемы и процитированы выше;
- **значения α, ϑ, α\* по каждому графу — UNVERIFIED и в сравнении не участвуют**;
- **пографовая сверка, которую требует бриф 3.a.3, невыполнима**, и это записано как
  факт, а не как пропуск.

Правило о недостижимом источнике применено буквально: то, что удалось прочитать,
процитировано; то, что не удалось, помечено и исключено из решающих сравнений.

## S12 — теоретическое основание отсева, найденное попутно

A. Cabello, L. E. Danielsen, A. J. López-Tarrida, J. R. Portillo,
*Basic exclusivity graphs in quantum correlations*, https://arxiv.org/abs/1211.5825 —
обращение 2026-08-20, выгрузка `sources/eprint_1211.5825`,
исходник `sources/ep1211/Fundamental_structures_17_afterpraproofs.tex`. Из аннотации:

> We prove that quantum theory only violates those NC inequalities whose exclusivity
> graphs contain, as induced subgraphs, odd cycles of length five or more, and/or their
> complements.

**Читается так:** Δ(G) > 0 влечёт наличие индуцированной нечётной дыры или антидыры
длины ≥ 5, то есть несовершенство G. Это ровно то направление, на котором стоит
звуковость нашего отсева F1 (совершенный ⇒ Δ = 0), и оно здесь получено независимо от
нас и раньше нас. **Обратное неверно**, и наши данные это показывают количественно:
на n = 8 несовершенных графов 3 312, а с Δ > 0 — только 498. Утверждение о
необходимости, не о достаточности.

---

## S7 — Knuth, «The Sandwich Theorem» (литчек Stage 7, выполнен ПОСЛЕ счёта)

D. E. Knuth, *The Sandwich Theorem*, Electronic Journal of Combinatorics **1** (1994),
#A1; препринт arXiv:math/9312214v1, 6 Dec 1993.
https://arxiv.org/abs/math/9312214 — обращение **2026-08-24**.
Выгрузка: `sources/knuth_sandwich_theorem.pdf` (49 страниц, 361 260 байт),
текст `sources/knuth_sandwich_theorem.txt`.

Порядок соблюдён по предрегистрации Stage 7 §7.d: блоки 7.a–7.c посчитаны и записаны
до того, как этот источник был открыт. Найденное ниже — **известное свойство,
применённое к новой задаче**, а не находка стадии.

### S7.1 — аддитивность ϑ на дизъюнктном объединении

`knuth_sandwich_theorem.txt` строки 973, 977:

> `18. The direct sum of graphs. Let G = G′ + G′′ be the graph on vertices`
>
> `ϑ(G, w) = ϑ(G′, w′) + ϑ(G′′, w′′) , (18.2)`

Строка 980: «`We can prove (18.2) by constructing orthogonal labelings (a, b)`» — далее
конструктивное доказательство, строки 980–1050.

### S7.2 — ϑ при соединении (join)

Строки 1052 и 1064:

> `19. The direct cosum of graphs. If G′ and G′′ are graphs on disjoint vertex sets V ′`
>
> `ϑ(G, w) = max ( ϑ(G′, w′), ϑ (G′′, w′′) )   (19.2)`

Строка 1055: «`This means u − −v in G if and only if either u − −v in G′ or u − −v in
G′′ or u and v belong to opposite vertex sets`» — то есть cosum есть соединение
(все перекрёстные пары смежны).

### S7.3 — что из этого следует для конструкции C_k

Конструкция C_k(G) из `PREREGISTRATION_STAGE7.md` §1 есть в точности

    C_k(G) = {v} cosum (G + K̄_{k−1}),

поэтому по (18.2) и (19.2)

    ϑ(C_k(G)) = max( ϑ({v}), ϑ(G) + ϑ(K̄_{k−1}) ) = max( 1, ϑ(G) + k − 1 )
              = ϑ(G) + k − 1,   так как ϑ(G) ≥ α(G) ≥ 1.

**Приоритет.** Обе формулы опубликованы Кнутом в 1993/1994 и восходят к Ловасу (1979);
новизны в них нет и мы её не заявляем. Новым в Stage 7 является только применение:
что верхние слои разложения по числу независимости целиком порождаются этим переносом,
и что граница наследования при n = 9 и n = 10 равна a\* = 5. Само неравенство H7
(D(n,a) ≥ T(n,a)) — прямое следствие S7.1 и S7.2, а не самостоятельный результат.

---

## S8 — Nie, Ranestad, Sturmfels: алгебраическая степень SDP (литчек Stage 7.1b, ПОСЛЕ формулировки)

J. Nie, K. Ranestad, B. Sturmfels, *The Algebraic Degree of Semidefinite Programming*,
Mathematical Programming **122** (2010) 379–405; препринт arXiv:math/0611562v3, 8 Sep 2008.
https://arxiv.org/abs/math/0611562 — обращение **2026-08-24**.
Выгрузка: `sources/nie_ranestad_sturmfels_sdp_degree.pdf` (23 страницы, 1 474 359 байт),
текст `sources/nie_ranestad_sturmfels_sdp_degree.txt`.

Порядок соблюдён: утверждение 7.1b.d об обрыве ряда замкнутых форм сформулировано и
закоммичено (`ae3ca4b`) прежде, чем этот источник был открыт.

### S8.1 — степень оптимума SDP и невыразимость в радикалах

Строки 98–103:

> `Our analysis shows that the algebraic degree of SDP equals six when m = 2 and n = 3.`
> `If the matrix B and the plane U are defined over Q then the coordinates of the optimal`
> `solution Ŷ are algebraic numbers of degree six. By Galois theory, the solution Ŷ cannot in`
> `general be expressed in terms of radicals. For any specific numerical instance we can use the`
> `command “galois” in maple to compute the Galois group, which is then typically found to`
> `be the symmetric group S6.`

### S8.2 — степень «обычно очень велика»

Строки 148–151:

> `The algebraic degree of semidefinite programming addresses the computational complexity`
> `at a fundamental level. To solve the semidefinite programming exactly essentially reduces`
> `to solve a class of univariate polynomial equations whose degrees are the algebraic degree.`
> `As we will see later in this paper, the algebraic degree is usually very big, even for some small`
> `problems.`

Строка 863 — конкретные значения при n = 6:

> `δ(6, 6, 4) = 1400 , δ (7, 6, 4) = 2040 , δ (8, 6, 4) = 2100 , δ (9, 6, 4) = 1470 .`

### S8.3 — что это подтверждает и чего не подтверждает

**Подтверждает** формулировку 7.1b.d: типичная алгебраическая степень оптимума SDP с
рациональными данными велика уже при матрицах 3×3 (шесть, с группой Галуа S₆ и без
выражения в радикалах) и исчисляется тысячами при 6×6. Ожидать замкнутых форм для
матриц 11×11 нет оснований; обрыв ряда на n = 11 — норма, а не неудача.

**Не подтверждает буквально**: результат относится к **типичной** (generic) SDP, а наша —
структурированная (ϑ), с нулями на рёбрах и следом 1, и потому не покрывается их
теоремами напрямую. Низкие степени при n ≤ 10 (от 1 до 4) — именно отклонение от
типичного, и объяснять их надо структурой и симметрией, а не общей теорией.

Наблюдение, записываемое как наблюдение и без пересчёта каких-либо корреляций:
|Aut| максимизаторов по ряду равен 10, 10, 14, 8, 12, 16 и **2** при n = 11. Граф,
на котором степень уходит за 48, — наименее симметричный из всех семи, то есть первый
в ряду, близкий к типичному в смысле S8.1–S8.2. Механизма отсюда не выводится.

---

## S9 — OEIS A001349, число связных графов (проверка счётов и оценки для n = 12)

*The On-Line Encyclopedia of Integer Sequences*, последовательность **A001349**,
«Number of simple connected graphs on n unlabeled nodes».
https://oeis.org/A001349 — обращение **2026-08-24**, выгрузка
`sources/oeis_A001349.json` (JSON, 16 633 байта).

| n | A001349 | наш счёт `geng -c -u n` |
|--:|---|---|
| 8 | 11 117 | 11 117 |
| 9 | 261 080 | 261 080 |
| 10 | 11 716 571 | 11 716 571 |
| 11 | 1 006 700 565 | 1 006 700 565 |
| 12 | **164 059 830 476** | не считалось |
| 13 | 50 335 907 869 219 | не считалось |

**Совпадение по всем четырём размерам, которые мы перебирали**, включая одиннадцать
вершин. Это независимая внешняя проверка полноты наших переборов — до сих пор она
опиралась только на согласие суммы по частям `res/mod` со счётом самого `geng`, то есть
на один и тот же инструмент с двух сторон.

Отсюда же берётся оценка стоимости n = 12, приводимая в `OPEN_PROBLEM.md`: наша
измеренная пропускная способность на семи процессах есть 1.402·10⁷ графов в час
(1 006 700 565 за 71.8 ч), значит 164 059 830 476 графов потребуют **≈ 11 700 часов,
то есть около 490 суток** на том же железе. Множитель между одиннадцатью и двенадцатью
вершинами — 163.

## S13 — литчек Stage 9 (выполнен ПОСЛЕ счёта, блок 9.d)

Порядок соблюдён: `PREREGISTRATION_STAGE9.md` запечатан коммитом `585a275`
(2026-08-26T11:40Z), все замеры 9.a закончены, и только после этого открыт поиск.
Дата обращения по всем пунктам ниже — **2026-08-26**.

### S13.1 — оговорка о типичности у Nie–Ranestad–Sturmfels

Тот же источник, что и §S8 (файл `sources/nie_ranestad_sturmfels_sdp_degree.pdf`,
md5 `14e0660d102011ddc228755c948c8c58`). Для Stage 9 решающей оказывается не таблица
степеней, а оговорка авторов о границах их результата. Строки 383–387:

> `This experiment highlights again the genericity hypothesis made throughout this paper.`
> `We shall always assume that the m-tuple (A1, ..., Am), the cost matrix C and vector b are`
> `generic. All results in this paper are only valid under this genericity hypothesis. Naturally,`
> `special phenomena will happen for special problem instances. For instance, the rank of the`
> `optimal matrix can be outside the Pataki interval. While such special instances are important`
> `for applications of SDP, we shall not address them in this present study.`

Таблица 2 (строка 863 того же файла) перепроверена независимо от §S8 прямым чтением
PDF: при n = 6 значения δ(6,6,4) = 1400, δ(7,6,4) = 2040, δ(8,6,4) = 2100,
δ(9,6,4) = 1470, а также δ(9,6,3) = 3812 — то есть диапазон «1400–2100» реален, но
не является верхней границей столбца. Степень 6 при S₆ относится к **m = 2, n = 3**,
где n — размер матрицы; это действительно матрицы 3×3.

**Что отсюда следует для Stage 9.** Наша SDP — не типичная: матрицы ограничений суть
0/1-шаблоны рёбер, след единичный. Авторы сами выводят такие задачи за рамки своих
теорем приведённой цитатой. Поэтому наши низкие степени **не противоречат** их
результату и не являются его опровержением; они лежат в области, которую их работа
явно не рассматривает. Всякая формулировка вида «наши степени на два-три порядка ниже
типичной» обязана нести эту оговорку рядом.

### S13.2 — мерил ли кто-нибудь алгебраическую степень ϑ

Поиск по запросам «algebraic degree Lovász theta function», «"algebraic degree"
"theta function" graph Lovász number minimal polynomial irrational», «Lovász theta
function rational values graph classes algebraic degree» (обращение 2026-08-26) не дал
ни одной работы, измеряющей алгебраическую степень ϑ по классу графов. Найденное
относится к вычислению значений (Sage, циркулянты, Paley), к характеризации ϑ через
производящие функции блужданий (arXiv:2501.15277), к оценкам на случайных графах.

**Формулируется как отрицательный результат поиска, а не как утверждение о литературе.**
Правило 0 не позволяет сказать «этого никто не делал»: отсутствие в доступных нам
источниках не есть отсутствие в литературе. Корректная запись: *в источниках,
достижимых нам на 2026-08-26, такого измерения не найдено.*

### S13.3 — известны ли классы графов с рациональным ϑ

Отдельные рациональные значения в литературе встречаются — например, числа Ловаса
графов Келлера включают 4, 6 и 28/3 (найдено поиском, самих работ мы не выгружали,
поэтому эти три числа помечаются `UNVERIFIED` и **не используются** ни в одном
сравнении). Характеризации классов с рациональным ϑ не найдено.

Наши собственные рациональные значения получены здесь и точны: ϑ = 11/3 у
максимизатора n = 9 и у трёх графов из первой пятёрки n = 10 (§S9 стадии 2), и
ϑ = α у всех графов с Δ = 0 по построению.

### S13.4 — степень SDP при наличии симметрии

Ожидание, записанное в `PREREGISTRATION_STAGE9.md` §9 до счёта, было: «это почти
наверняка существует». Поиск (запрос «symmetry reduction semidefinite programming
algebraic degree automorphism group lower degree», обращение 2026-08-26) находит
обширную классическую литературу по **редукции** SDP по симметрии — Gatermann–Parrilo,
де Клерк и соавторы, Schrijver, — где группа действует на матрицах задачи и размер
матриц падает до числа орбит. Это про **вычислительный** выигрыш.

Работы, связывающей **алгебраическую степень оптимума** с порядком группы
автоморфизмов, найти не удалось. Встреченный в выдаче термин «singularity degree
остаётся тем же после редукции по симметрии» относится к другому понятию (степень
сингулярности в смысле facial reduction) и **не** является ответом на наш вопрос;
смешивать их нельзя.

**Как это ложится на исход 9.b.** Гипотеза H9-C (степень определяется симметрией)
опровергнута нашими данными: |ρ| < 0.20 на трёх размерах из четырёх, знаки не
согласованы. Литчек не даёт основания считать, что мы опровергли нечто установленное:
такой связи в найденных источниках не утверждается. То есть наш вклад здесь —
**измерение на конкретном классе**, а не опровержение известной теоремы и не открытие
новой связи. Записано ровно так, как требовал §9 предрегистрации, и исход этого
не меняет.

---
