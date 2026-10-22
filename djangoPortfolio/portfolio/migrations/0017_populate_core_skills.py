from django.db import migrations

INITIAL_CATEGORIES = [
    {
        "name": "Systems & Low-Level",
        "name_en": "Systems & Low-Level",
        "name_es": "Sistemas y Bajo Nivel",
        "order": 1,
        "skills": [
            {"name": "C / C++", "name_en": "C / C++", "name_es": "C / C++"},
            {"name": "POSIX Sockets", "name_en": "POSIX Sockets", "name_es": "Sockets POSIX"},
            {"name": "Multithreading", "name_en": "Multithreading", "name_es": "Multihilos"},
            {"name": "Linux System Calls", "name_en": "Linux System Calls", "name_es": "Llamadas al Sistema Linux"},
            {"name": "Memory Management", "name_en": "Memory Management", "name_es": "Gestión de Memoria"},
        ],
    },
    {
        "name": "Backend & Data Architecture",
        "name_en": "Backend & Data Architecture",
        "name_es": "Arquitectura Backend y Datos",
        "order": 2,
        "skills": [
            {"name": "Python", "name_en": "Python", "name_es": "Python"},
            {"name": "Django", "name_en": "Django", "name_es": "Django"},
            {"name": "PostgreSQL", "name_en": "PostgreSQL", "name_es": "PostgreSQL"},
            {"name": "Huey Task Queues", "name_en": "Huey Task Queues", "name_es": "Colas de Tareas Huey"},
            {"name": "RESTful APIs", "name_en": "RESTful APIs", "name_es": "APIs RESTful"},
        ],
    },
    {
        "name": "Hardened Infrastructure",
        "name_en": "Hardened Infrastructure",
        "name_es": "Infraestructura Blindada",
        "order": 3,
        "skills": [
            {"name": "Docker & Containers", "name_en": "Docker & Containers", "name_es": "Docker y Contenedores"},
            {"name": "Nginx Reverse Proxy", "name_en": "Nginx Reverse Proxy", "name_es": "Proxy Inverso Nginx"},
            {"name": "ClamAV Security Daemon", "name_en": "ClamAV Security Daemon", "name_es": "Daemon de Seguridad ClamAV"},
            {"name": "Linux Server Admin", "name_en": "Linux Server Admin", "name_es": "Administración de Servidores Linux"},
            {"name": "Raspberry Pi Edge Nodes", "name_en": "Raspberry Pi Edge Nodes", "name_es": "Nodos Edge Raspberry Pi"},
        ],
    },
    {
        "name": "Applied Cryptography & Telematics",
        "name_en": "Applied Cryptography & Telematics",
        "name_es": "Criptografía Aplicada y Telemática",
        "order": 4,
        "skills": [
            {"name": "ElGamal Asymmetric Crypto", "name_en": "ElGamal Asymmetric Crypto", "name_es": "Criptografía Asimétrica ElGamal"},
            {"name": "Zero-Knowledge Verification", "name_en": "Zero-Knowledge Verification", "name_es": "Verificación Conocimiento Cero"},
            {"name": "Custom Binary Protocols", "name_en": "Custom Binary Protocols", "name_es": "Protocolos Binarios Propios"},
            {"name": "UDP/TCP Telemetry Streams", "name_en": "UDP/TCP Telemetry Streams", "name_es": "Flujos de Telemetría UDP/TCP"},
            {"name": "Algorithmic Problem Solving", "name_en": "Algorithmic Problem Solving", "name_es": "Resolución Algorítmica de Problemas"},
        ],
    },
]


def populate_core_skills(apps, schema_editor):
    SkillCategory = apps.get_model("portfolio", "SkillCategory")
    CoreSkill = apps.get_model("portfolio", "CoreSkill")

    for cat_data in INITIAL_CATEGORIES:
        skills_data = cat_data.pop("skills")
        category, _ = SkillCategory.objects.get_or_create(
            name=cat_data["name"],
            defaults=cat_data,
        )
        for skill_data in skills_data:
            CoreSkill.objects.get_or_create(
                category=category,
                name=skill_data["name"],
                defaults=skill_data,
            )


def reverse_populate(apps, schema_editor):
    SkillCategory = apps.get_model("portfolio", "SkillCategory")
    SkillCategory.objects.filter(
        name__in=[cat["name"] for cat in INITIAL_CATEGORIES]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("portfolio", "0016_nodeheartbeat_status"),
    ]

    operations = [
        migrations.RunPython(populate_core_skills, reverse_populate),
    ]
