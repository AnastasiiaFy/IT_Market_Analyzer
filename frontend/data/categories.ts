// data/categories.ts

export const categoryGroups = [
  {
    title: "Розробка",
    items: [
      {
        slug: "frontend-developer",
        label: "Frontend Developer",
      },
      {
        slug: "backend-developer",
        label: "Backend Developer",
      },
      {
        slug: "full-stack-developer",
        label: "Full Stack Developer",
      },
      {
        slug: "mobile-developer",
        label: "Mobile Developer",
      },
      {
        slug: "java-developer",
        label: "Java Developer",
      },
      {
        slug: "python-developer",
        label: "Python Developer",
      },
      {
        slug: "dotnet-developer",
        label: ".NET Developer",
      },
      {
        slug: "software-embedded-engineer",
        label: "Software / Embedded Engineer",
      },
    ],
  },

  {
    title: "Дані та аналітика",
    items: [
      {
        slug: "business-analyst",
        label: "Business Analyst",
      },
      {
        slug: "data-analyst",
        label: "Data Analyst",
      },
      {
        slug: "data-engineer",
        label: "Data Engineer",
      },
      {
        slug: "ml-ai-engineer",
        label: "ML / AI Engineer",
      },
    ],
  },

  {
    title: "Інфраструктура",
    items: [
      {
        slug: "devops-sre-engineer",
        label: "DevOps / SRE Engineer",
      },
      {
        slug: "system-administrator-network-engineer",
        label: "System Administrator / Network Engineer",
      },
    ],
  },

  {
    title: "Якість",
    items: [
      {
        slug: "qa-automation-engineer",
        label: "QA Automation Engineer",
      },
      {
        slug: "qa-manual-engineer",
        label: "QA Manual Engineer",
      },
    ],
  },

  {
    title: "Дизайн",
    items: [
      {
        slug: "ux-ui-designer",
        label: "UX/UI Designer",
      },
    ],
  },
] as const;



export function findCategoryBySlug(slug: string) {
  for (const group of categoryGroups) {
    const item = group.items.find((i) => i.slug === slug);

    if (item) {
      return item;
    }
  }

  return null;
}