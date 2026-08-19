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
