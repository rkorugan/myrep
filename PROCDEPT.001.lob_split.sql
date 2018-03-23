CREATE OR REPLACE PROCEDURE procdept(deptno integer) DYNAMIC RESULT SETS 1 LANGUAGE SQL SPECIFIC TAECheckExhaustion BEGIN DECLARE v_deptno VARCHAR(20);
DECLARE v_deptname VARCHAR(20);
DECLARE v_mgrno INTEGER;
DECLARE v_location VARCHAR(300);
DECLARE V_EMPNO VARCHAR(30);
DECLARE V_FIRSTNME VARCHAR(30);
DECLARE V_LASTNAME VARCHAR(30);
DECLARE ECUR CURSOR FOR SELECT * FROM EMPLOYEE;
DECLARE DCUR CURSOR FOR SELECT * FROM DEPARTMENT;
SET v_deptno='A00';
IF DEPTNO IS NOT NULL THEN SELECT deptname INTO v_deptname FROM department WHERE deptno=v_deptno;
END IF;
SELECT LOCATION INTO v_location FROM department WHERE deptno=v_deptno;
SELECT MGRNO INTO v_mgrno FROM department WHERE deptno=v_deptno;
SELECT E.EMPNO, E.FIRSTNME, E.LASTNAME INTO V_EMPNO, V_FIRSTNME, V_LASTNAME FROM EMPLOYEE E, DEPARTMENT D WHERE E.WORKDEPT=D.DEPTNO AND E.EMPNO='000050';
IF(1=2) THEN UPDATE DEPARTMENT SET LOCATION='BLR' WHERE DEPTNO=v_deptno;
UPDATE DEPARTMENT A SET LOCATION=v_location;
END IF;
DELETE FROM DEPARTMENT WHERE DEPTNAME = (SELECT DEPTNAME FROM DEPARTMENT WHERE DEPTNO='B01');
INSERT INTO DB2ADMIN.DEPARTMENT (DEPTNO, DEPTNAME, MGRNO, ADMRDEPT, LOCATION) VALUES ('X00', 'SPIFFY COMPUTER SERVICE DIV.', '000010', 'A00', NULL);
INSERT INTO DB2ADMIN.DEPARTMENT (DEPTNO, DEPTNAME, MGRNO, ADMRDEPT, LOCATION) VALUES ('z00', 'SPIFFY COMPUTER SERVICE DIV.', '000010', 'A00', NULL);
END
