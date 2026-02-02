# import re

# # -------- NORMALIZE TEXT --------
# def normalize(text):
#     text = text.lower()
#     text = re.sub(r"[^a-z0-9\s]", " ", text)
#     return text


# # -------- SKILL SYNONYMS (VERY IMPORTANT) --------
# SKILL_SYNONYMS = {
#     "python": ["python"],
#     "machine learning": ["machine learning", "ml", "ai"],
#     "data analysis": ["data analysis", "analytics", "data"],
#     "sql": ["sql", "database"],
#     "git": ["git", "version control"],
#     "docker": ["docker", "containers"],
#     "aws": ["aws", "cloud"],
#     "devops": ["devops", "ci cd", "pipeline"]
# }


# # def rank_jobs_by_percentage(resume_skills, jobs, threshold=40):
# #     if not resume_skills or not jobs:
# #         return []

# #     import re

# #     def normalize(text):
# #         text = text.lower()
# #         text = re.sub(r"[^a-z0-9\s]", " ", text)
# #         return text

# #     SKILL_SYNONYMS = {
# #         "python": ["python"],
# #         "machine learning": ["machine learning", "ml", "ai"],
# #         "data analysis": ["data analysis", "analytics", "data"],
# #         "sql": ["sql", "database"],
# #         "git": ["git", "version control"],
# #         "docker": ["docker", "containers"],
# #         "aws": ["aws", "cloud"],
# #         "devops": ["devops", "ci cd", "pipeline"]
# #     }

# #     expanded_skills = set()
# #     for skill in resume_skills:
# #         skill = skill.lower()
# #         expanded_skills.update(SKILL_SYNONYMS.get(skill, [skill]))

# #     total_skills = len(expanded_skills)

# #     ranked_jobs = []

# #     for job in jobs:
# #         text = normalize(job.get("title", "") + " " + job.get("description", ""))

# #         matched = set()
# #         for skill in expanded_skills:
# #             if skill in text:
# #                 matched.add(skill)

# #         match_percentage = round((len(matched) / total_skills) * 100, 2)

# #         # ✅ FILTER HERE
# #         if match_percentage >= threshold:
# #             ranked_jobs.append({
# #                 **job,
# #                 "match_percentage": match_percentage,
# #                 "matched_skills": list(matched)
# #             })

# #     return sorted(ranked_jobs, key=lambda x: x["match_percentage"], reverse=True)



# def rank_jobs_by_percentage(resume_skills, jobs):
#     results = []

#     resume_skills = set([s.lower() for s in resume_skills])

#     for job in jobs:
#         job_text = (
#             job.get("title","") + " " +
#             job.get("description","")
#         ).lower()

#         matched = [s for s in resume_skills if s in job_text]

#         if resume_skills:
#             match_percent = round(len(matched) / len(resume_skills) * 100, 2)
#         else:
#             match_percent = 0

#         # 🔥 CHANGE HERE
#         if match_percent >= 10:   # was 40 earlier
#             results.append({
#                 "title": job["title"],
#                 "company": job["company"],
#                 "location": job.get("location",""),
#                 "match": match_percent,
#                 "skills": matched,
#                 "url": job.get("url")
#             })

#     return sorted(results, key=lambda x: x["match"], reverse=True)[:25]



import re

def rank_jobs_by_percentage(resume_skills, jobs):
    results = []

    if not resume_skills or not jobs:
        return results

    resume_skills = set([s.lower() for s in resume_skills])

    for job in jobs:
        job_text = (
            job.get("title", "") + " " +
            job.get("description", "")
        ).lower()

        matched = [s for s in resume_skills if s in job_text]

        match_percent = round((len(matched) / len(resume_skills)) * 100, 2)

        # 🔥 keep threshold LOW for real APIs
        if match_percent >= 10:
            results.append({
                "title": job.get("title", ""),
                "company": job.get("company", ""),
                "location": job.get("location", "Not specified"),
                "match_percentage": match_percent,     # ✅ STANDARD KEY
                "matched_skills": matched,             # ✅ STANDARD KEY
                "url": job.get("url")
            })

    return sorted(results, key=lambda x: x["match_percentage"], reverse=True)[:25]
