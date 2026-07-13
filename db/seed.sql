-- ============================================================
-- SEED SQL para Munigo - Ejecutar en Supabase SQL Editor
-- ============================================================

-- Limpiar tablas en orden correcto (respetar foreign keys)
TRUNCATE TABLE
    inspections_inspection,
    notifications_notification,
    procedures_attacheddocument,
    procedures_appointment,
    procedures_procedurerequirement,
    procedures_casefile,
    procedures_requirement,
    organizations_establishment,
    organizations_company_citizens,
    organizations_company,
    users_employee,
    users_citizen,
    users_user
CASCADE;

-- Resetear secuencias
ALTER SEQUENCE users_user_id_seq RESTART WITH 1;
ALTER SEQUENCE users_citizen_id_seq RESTART WITH 1;
ALTER SEQUENCE users_employee_id_seq RESTART WITH 1;
ALTER SEQUENCE organizations_establishment_id_seq RESTART WITH 1;
ALTER SEQUENCE procedures_requirement_id_seq RESTART WITH 1;
ALTER SEQUENCE procedures_casefile_id_seq RESTART WITH 1;
ALTER SEQUENCE procedures_procedurerequirement_id_seq RESTART WITH 1;
ALTER SEQUENCE procedures_appointment_id_seq RESTART WITH 1;
ALTER SEQUENCE inspections_inspection_id_seq RESTART WITH 1;
ALTER SEQUENCE notifications_notification_id_seq RESTART WITH 1;

-- ============================================================
-- 1. USUARIOS
-- ============================================================

-- Password: admin123
INSERT INTO users_user (id, password, username, email, first_name, last_name, role, is_staff, is_superuser, is_active, date_joined)
VALUES
(1, 'pbkdf2_sha256$1000000$eRkL6vcvybRQVeFMzqWaN4$plUeE3AGzGzZaa997pJHb8AdtpCgoe8yP+oYW9uCn/g=', 'admin', 'admin@munigo.gob.ec', 'Admin', 'Munigo', 'EMPLOYEE', true, true, true, NOW()),
(2, 'pbkdf2_sha256$1000000$TOURW7Km47IgWj8hW3aKzP$nXgHBY0SOuqIUfprMkKK2a18ZXVUHE/u9wINATl2Ib8=', 'ciudadano1', 'ciudadano1@test.com', 'Juan', 'Perez', 'CITIZEN', false, false, true, NOW()),
(3, 'pbkdf2_sha256$1000000$TOURW7Km47IgWj8hW3aKzP$nXgHBY0SOuqIUfprMkKK2a18ZXVUHE/u9wINATl2Ib8=', 'ciudadano2', 'ciudadano2@test.com', 'Maria', 'Lopez', 'CITIZEN', false, false, true, NOW()),
(4, 'pbkdf2_sha256$1000000$TOURW7Km47IgWj8hW3aKzP$nXgHBY0SOuqIUfprMkKK2a18ZXVUHE/u9wINATl2Ib8=', 'gerente', 'gerente@test.com', 'Carlos', 'Garcia', 'EMPLOYEE', false, false, true, NOW()),
(5, 'pbkdf2_sha256$1000000$TOURW7Km47IgWj8hW3aKzP$nXgHBY0SOuqIUfprMkKK2a18ZXVUHE/u9wINATl2Ib8=', 'inspector', 'inspector@test.com', 'Ana', 'Torres', 'EMPLOYEE', false, false, true, NOW()),
(6, 'pbkdf2_sha256$1000000$TOURW7Km47IgWj8hW3aKzP$nXgHBY0SOuqIUfprMkKK2a18ZXVUHE/u9wINATl2Ib8=', 'funcionario', 'funcionario@test.com', 'Luis', 'Martinez', 'EMPLOYEE', false, false, true, NOW());

SELECT setval('users_user_id_seq', 6);

-- ============================================================
-- 2. CIUDADANOS
-- ============================================================

INSERT INTO users_citizen (id, user_id, document_type, document_number)
VALUES
(1, 2, 'DNI', '0102030405'),
(2, 3, 'DNI', '0506070809'),
(3, 4, 'DNI', '09999999990'),
(4, 5, 'DNI', '0105060708'),
(5, 6, 'DNI', '0106070809');

SELECT setval('users_citizen_id_seq', 5);

-- ============================================================
-- 3. EMPLEADOS
-- ============================================================

INSERT INTO users_employee (id, citizen_id, position, area)
VALUES
(1, 3, 'GERENTE', 'ADMINISTRACION'),
(2, 4, 'INSPECTOR', 'FISCALIZACION'),
(3, 5, 'FUNCIONARIO', 'LICENCIAS');

SELECT setval('users_employee_id_seq', 3);

-- ============================================================
-- 4. EMPRESAS
-- ============================================================

INSERT INTO organizations_company (id, business_name, ruc)
VALUES
(1, 'Restaurante El Sabor', '09912345671'),
(2, 'Comercial TodoFarma', '09976543210');

-- Relación M2M empresa-citizens
INSERT INTO organizations_company_citizens (company_id, citizen_id)
VALUES
(1, 1),
(2, 2);

-- ============================================================
-- 5. ESTABLECIMIENTOS
-- ============================================================

INSERT INTO organizations_establishment (id, company_id, name, address, business_category, square_meters)
VALUES
(1, 1, 'El Sabor - Sede Central', 'Av. 9 de Octubre 123, Guayaquil', 'RESTAURANT', 120),
(2, 2, 'TodoFarma - Centro', 'Calle Largo 456, Guayaquil', 'COMERCIO', 80),
(3, 2, 'TodoFarma - Norte', 'Av. Francisco de Orellana 789, Guayaquil', 'COMERCIO', 250);

SELECT setval('organizations_establishment_id_seq', 3);

-- ============================================================
-- 6. REQUISITOS (Catálogo)
-- ============================================================

INSERT INTO procedures_requirement (id, name, description, allowed_formats, is_required, procedure_type)
VALUES
(1, 'Planos de distribución', 'Planos arquitectónicos del local a escala 1:100', '["PDF"]', true, 'LICENCIA_DE_FUNCIONAMIENTO'),
(2, 'Certificado de zonificación', 'Documento que indica la zonificación del predio', '["PDF"]', true, 'LICENCIA_DE_FUNCIONAMIENTO'),
(3, 'Póliza de responsabilidad civil', 'Póliza vigente de responsabilidad civil', '["PDF"]', true, 'LICENCIA_DE_FUNCIONAMIENTO'),
(4, 'Fotografía del local', 'Fotografía reciente del local comercial', '["PDF","PNG","JPG"]', true, 'LICENCIA_DE_FUNCIONAMIENTO'),
(5, 'Pago de derechos municipales', 'Comprobante de pago de la tasa municipal', '["PDF"]', true, 'LICENCIA_DE_FUNCIONAMIENTO'),
(6, 'Certificado ITSE vigente', 'Certificado de Inspección Técnica de Seguridad y Salud en el Trabajo', '["PDF"]', true, 'ITSE'),
(7, 'Plan de emergencia', 'Plan de emergencia y evacuación del establecimiento', '["PDF"]', true, 'ITSE'),
(8, 'Capacitación de personal', 'Constancia de capacitación en seguridad laboral', '["PDF","PNG","JPG"]', false, 'ITSE');

SELECT setval('procedures_requirement_id_seq', 8);
