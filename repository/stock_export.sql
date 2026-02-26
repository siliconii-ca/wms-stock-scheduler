-- 재고 현황 조회 쿼리
DECLARE @CompCd		varchar(10)  = 'CO000001'
	,@BranchCd		INT = 0 

CREATE TABLE #TEMP_PROD (
	prod_cd varchar(50) 
	,prod_nm nvarchar(200)
	,brand_nm nvarchar(50)
	,prod_use_yn varchar(1)
)

DECLARE @Err INT;
DECLARE @sMSG NVARCHAR(90);


CREATE CLUSTERED INDEX IX_TEMP_PROD ON #TEMP_PROD(prod_cd)
UPDATE STATISTICS #TEMP_PROD

INSERT INTO #TEMP_PROD (prod_cd,prod_nm,brand_nm,prod_use_yn)
SELECT p.prod_cd , pl.prod_nm , bl.brand_nm ,p.use_yn
FROM CSMS.dbo.TB_PROD P WITH (NOLOCK)
INNER JOIN CSMS.dbo.TB_PROD_LANG PL WITH (NOLOCK) ON p.prod_cd = pl.prod_cd AND pl.lang_cd = 'KOR'
INNER JOIN CSMS.dbo.TB_BRAND_LANG bL WITH (NOLOCK) ON p.brand_cd = bl.brand_cd and  bl.lang_cd = 'KOR'

;
WITH CTE_CMS_STOCK AS (
	SELECT p.prod_cd , p.prod_nm , p.brand_nm ,p.prod_use_yn
			,ISNULL(cms.qty,0) as cms_total_qty
			,CASE @CompCd  WHEN 'CO000001' THEN ISNULL(agv4.base_qty,0) +ISNULL(loc.qty,0) +ISNULL(agv1.in_qty - agv1.out_qty,0) 
				WHEN 'CO000007' THEN ISNULL(loc_usa.qty,0) 
				END AS wms_total_qty
			,ISNULL(w.io_qty,0) as waiting_qty
			, CASE @CompCd  WHEN 'CO000001' THEN ISNULL(loc.qty,0) 
				WHEN 'CO000007' THEN ISNULL(loc_usa.qty,0) 
				END AS loc_qty
			,ISNULL(agv1.in_qty - agv1.out_qty,0)  AS agv1_qty
			,ISNULL(agv4.base_qty,0) AS agv4_qty
			,CASE WHEN w.io_qty IS NULL THEN 0 ELSE 1 END AS has_waiting_qty
	FROM #TEMP_PROD P 
	OUTER APPLY (
		SELECT SUM(st.stock_qty) AS qty
		FROM BASE_DB.dbo.TB_COMP A WITH (NOLOCK)
		INNER JOIN BASE_DB.dbo.TB_BRANCH C WITH(NOLOCK) ON A.comp_cd = C.comp_cd
		INNER JOIN BASE_DB.dbo.TB_LOCATION_BRANCH D WITH(NOLOCK) ON c.branch_cd = d.branch_cd
		INNER JOIN BASE_DB.dbo.TB_WRHS W WITH(NOLOCK) ON d.whouse_cd = w.whouse_cd 
															-- trouble 창고 제외
															AND w.whouse_nm not like 'TROUBLE%'
		INNER JOIN IMS.dbo.TB_STOCK ST WITH(NOLOCK) ON w.whouse_cd = st.whouse_cd
		WHERE A.comp_cd = @CompCd AND c.branch_cd = @BranchCd AND  st.prod_cd = p.prod_cd  AND st.trbl_yn =0
		GROUP BY st.prod_cd		
	) cms
	OUTER APPLY (
		SELECT SUM(qty) as qty 
		FROM  CSMS_DB_MIRROR.dbo.TB_LOCATION_DTL a WITH(NOLOCK)
		INNER JOIN CSMS_DB_MIRROR.dbo.TB_LOCATION_TYPE B WITH (NOLOCK) ON a.loc_barcode = b.loc_barcode
		-- 본사 재고조정존 제외 처리 
		WHERE @BranchCd = 0 AND a.prod_cd = p.prod_cd and b.loc_barcode != '803025101000'
		GROUP BY a.prod_cd 	
	) loc
	OUTER APPLY (
		SELECT SUM(qty) as qty 
		FROM  CMSGLOBAL.dbo.TB_LOCATION_DTL_USA a WITH(NOLOCK)
		INNER JOIN CMSGLOBAL.dbo.TB_LOCATION_TYPE_USA B WITH (NOLOCK) ON a.loc_barcode = b.loc_barcode
		-- 본사 재고조정존 제외 처리 
		WHERE b.branch_cd = @BranchCd AND a.prod_cd = p.prod_cd 
		GROUP BY a.prod_cd 	
	) loc_usa
	LEFT JOIN CSMS_DB_MIRROR.dbo.TB_WS_AGV_STOCK agv4 WITH (NOLOCK) ON agv4.prod_cd = p.prod_cd AND @BranchCd = 0 
	LEFT JOIN CSMS_DB_MIRROR.dbo.TB_STOCK_AGV agv1 WITH(NOLOCK)  ON agv1.prod_cd = p.prod_cd AND @BranchCd = 0 
	OUTER APPLY (
		SELECT SUM(io_qty) as io_qty
		FROM CMSGLOBAL.dbo.TB_WMS_STOCK_WAITING WITH(NOLOCK)
		WHERE branch_cd = @BranchCd AND prod_cd = p.prod_cd
		GROUP BY prod_cd,branch_cd
	) w
)
SELECT a.prod_cd
		,a.prod_nm
		,a.brand_nm
		,a.prod_use_yn
		,a.cms_total_qty
		,a.wms_total_qty
		,a.agv1_qty
		,a.agv4_qty
		,a.loc_qty
		,a.waiting_qty
		,a.has_waiting_qty
FROM CTE_CMS_STOCK A
WHERE NOT (cms_total_qty = 0 AND wms_total_qty = 0 AND has_waiting_qty = 0)

