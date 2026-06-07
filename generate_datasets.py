import csv
import random
import os
import re

random.seed(42)

# ============================================================
#  HELPER FUNCTIONS
# ============================================================

def levenshtein_distance(s1: str, s2: str) -> int:
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def calculate_similarity(s1: str, s2: str) -> float:
    # Jaccard similarity of words
    w1 = set(s1.lower().split())
    w2 = set(s2.lower().split())
    if not w1 or not w2:
        return 0.0
    return len(w1 & w2) / len(w1 | w2)

# ============================================================
#  MUTABLE DATA ARRAYS FOR SYNTHESIS
# ============================================================

COMPANIES = [
    "Google", "Microsoft", "Amazon", "Flipkart", "Swiggy", "Zomato",
    "Paytm", "Razorpay", "PhonePe", "CRED", "Zepto", "Meesho",
    "TCS", "Infosys", "Wipro", "HCL", "Accenture", "Deloitte",
    "IBM", "Myntra", "Ola", "Byju's", "Lenskart", "Dream11"
]

SKILLS = [
    "Python", "Java", "React", "Node.js", "Django", "Flask",
    "Machine Learning", "Data Science", "SQL", "MongoDB",
    "TypeScript", "Angular", "Vue.js", "Docker", "AWS"
]

STIPENDS = ["5000", "10000", "15000", "20000", "25000", "30000"]

LEGIT_URLS = [
    "https://careers.google.com", "https://careers.microsoft.com",
    "https://amazon.jobs", "https://careers.flipkart.com",
    "https://careers.swiggy.com", "https://careers.zomato.com",
    "https://nextstep.tcs.com", "https://careers.infosys.com",
    "https://internshala.com", "https://linkedin.com/jobs"
]

# ============================================================
#  TEMPLATE DEFINITIONS & TRAIN/TEST SPLIT
# ============================================================

TEMPLATES = {
    "linkedin_networking": [
        "Hi! Let's connect on LinkedIn. I've been following your work in {skill}.",
        "Thanks for connecting! Looking forward to learning from your {skill} experience.",
        "Great profile! Your {skill} projects are impressive. Let's stay connected.",
        "Interested in your career journey. Would love to connect and learn more.",
        "Nice to connect with you! I see you're working on {skill} at {company}.",
        "Saw your post about {skill}. Really insightful. Let's connect!",
        "Hi, we have mutual connections. Would love to add you to my network.",
        "Following your work on {skill}. Your insights are valuable to the community.",
        "Congratulations on your new role at {company}! Let's stay connected.",
        "Your LinkedIn profile caught my attention. Great work in {skill}.",
        "Hello! I'm a {skill} enthusiast too. Let's connect and share knowledge.",
        "Impressed by your experience in {skill}. Would love to be part of your network.",
        "Hi, I noticed we both work in {skill}. Connection request sent!",
        "Great to see your contributions to the {skill} community on LinkedIn.",
        "Looking forward to connecting with professionals like you in {skill}.",
        "Your article on {skill} was really helpful. Sending a connection request.",
        "Hi! I'm building my professional network in {skill}. Let's connect.",
        "Saw you attended the {skill} conference. Would love to discuss insights.",
        "Your career path from {skill} to {company} is inspiring. Let's connect!",
        "Connection request: I admire your {skill} portfolio. Let's network!",
    ],
    "recruiter_update": [
        "Your application for {skill} intern at {company} has been received. We will review it shortly.",
        "Application status update: Your profile is under review for the {skill} position at {company}.",
        "Congratulations! You have been shortlisted for the {skill} internship at {company}. Next steps will follow.",
        "Interview scheduled: {skill} intern role at {company}. Please check your email for details.",
        "Assessment link shared for {company} {skill} internship. Complete within 3 days.",
        "We will update you next week regarding your {skill} application at {company}.",
        "Hi, this is from {company} recruitment team. Your application for {skill} role is being processed.",
        "Your interview for {skill} intern at {company} is confirmed for next Monday at 10 AM.",
        "Status: Your {company} {skill} internship application has moved to the next round.",
        "Talent acquisition update from {company}: We're reviewing your {skill} profile.",
        "You've cleared the aptitude test for {company} {skill} internship. HR will contact you soon.",
        "Recruitment drive update: {company} is reviewing all {skill} applications this week.",
        "Thank you for applying to {company}. Your {skill} application is in the selection pipeline.",
        "Hi, the hiring manager at {company} has reviewed your {skill} resume. Feedback coming soon.",
        "Good news! You've been selected for the technical round at {company} for {skill} intern.",
        "Your candidature for {company} {skill} internship is progressing well. Stay tuned.",
        "Interview reminder: Your {company} {skill} interview is tomorrow at 2 PM.",
        "We are pleased to inform you that your {skill} profile matches our requirements at {company}.",
        "Application update: {company} HR team has scheduled your {skill} interview for this Friday.",
        "Offer letter for {skill} intern at {company} has been sent to your registered email.",
    ],
    "campus_ambassador": [
        "Congratulations! You have been selected as Campus Ambassador for {company}.",
        "Campus coordinator application approved for {company} ambassador program.",
        "Join the {company} Campus Ambassador onboarding session this Saturday.",
        "Fill the onboarding form for {company} campus representative program.",
        "Welcome to {company} Campus Ambassador Program! Onboarding starts next week.",
        "Selected as {company} campus lead for your college. Training begins shortly.",
        "{company} Campus Ambassador: Your welcome kit will be dispatched shortly.",
        "Campus partner program update: {company} has approved your application.",
        "Brand ambassador selection confirmed for {company}. Training session next Monday.",
        "College representative for {company}: Please submit your college ID for verification.",
        "Your {company} campus coordinator role starts from next semester.",
        "{company} campus ambassador meeting scheduled for Friday at 4 PM via Google Meet.",
        "Welcome aboard as {company} campus representative! Check the dashboard.",
        "Campus ambassador benefits: {company} offers certificates and goodies.",
        "Hi! Your application for {company} campus brand ambassador has been accepted.",
        "Campus Ambassador task: Share the poster with your placement cell.",
    ],
    "whatsapp_onboarding": [
        "WhatsApp group created for {company} interns. Join link will be shared by HR.",
        "Join the {company} intern onboarding WhatsApp group for daily updates.",
        "Orientation session tomorrow at 10 AM. Details shared in the WhatsApp group.",
        "{company} intern WhatsApp group: Welcome! Please introduce yourself.",
        "Hi interns! The WhatsApp group for {company} {skill} batch has been set up.",
        "Onboarding update: Please join the {company} WhatsApp group for joining formalities.",
        "Welcome aboard! {company} intern induction details will be shared via WhatsApp.",
        "Team introduction: Your {company} reporting manager will message you on WhatsApp.",
        "Day one instructions will be shared in the {company} intern WhatsApp group tomorrow.",
        "Hi, this is HR from {company}. Adding you to the intern WhatsApp coordination group.",
        "{company} joining kit details have been shared in the WhatsApp group.",
        "WhatsApp group for {company} {skill} interns is now active. Welcome!",
        "Orientation schedule shared via WhatsApp. {company} intern batch starts Monday.",
        "Please save this number. All {company} intern updates will come via WhatsApp.",
        "Welcome to {company}! Your mentor will reach out via WhatsApp for prep.",
    ],
    "telegram_legit": [
        "Telegram channel created for {company} internship announcements. No payment needed.",
        "Join our Telegram group for {company} interview updates and schedule changes.",
        "All {company} intern updates will be posted on our official Telegram channel.",
        "{company} placement cell Telegram group: Share your doubts. No charges apply.",
        "Telegram group for {skill} study resources and {company} prep materials.",
        "Hi! The {company} intern Telegram group is for announcements only. No spam please.",
        "Official Telegram channel for {company} recruitment drive updates. Stay tuned.",
        "{company} Telegram group: Interview tips, mock tests, and free resources.",
        "Join the Telegram channel for {company} campus hiring updates. Free resources inside.",
        "Telegram notification: {company} has posted a new {skill} internship opening.",
        "Your {company} interview prep materials are shared in the Telegram group.",
        "Telegram update: {company} internship results will be announced tomorrow.",
    ],
    "course_promotion": [
        "Resume support and mock interviews available for {skill} roles. Free for students.",
        "Live mentor sessions on {skill} every weekend. Build your portfolio. No fee.",
        "Placement assistance program for {skill} freshers. Guidance from industry mentors.",
        "MERN Stack training with live projects. Certificate provided. Learn {skill}.",
        "{skill} bootcamp: 8 weeks intensive training. Placement assistance included.",
        "Career guidance webinar on {skill} career paths. Free registration.",
        "Workshop: Learn {skill} from scratch. Hands-on projects. Certificate included.",
        "{skill} masterclass by {company} engineers. Live Q&A session included.",
        "Full Stack {skill} training program. Build real-world projects. Mentor support.",
        "Skill development program in {skill}. Industry-relevant curriculum.",
        "Free webinar: How to crack {company} {skill} interviews. Register now.",
        "{skill} certification course with hands-on labs. Completion certificate provided.",
    ],
    "startup_hiring": [
        "Urgent hiring: {skill} intern at our growing startup. Work from home. No fee.",
        "Immediate joiners preferred for {skill} role. Remote internship. Stipend {stipend} per month.",
        "Student interns welcome! {skill} position at early-stage startup. Flexible hours.",
        "Work from home {skill} internship. Startup environment. Learn and grow. No payment required.",
        "Hiring {skill} interns for our fast-growing startup. Stipend {stipend} per month. Apply now.",
        "Remote {skill} internship at seed-funded startup. Real projects. Certificate provided.",
        "We're a growing team looking for {skill} interns. WFH. Stipend provided. No charges.",
        "Startup hiring: {skill} intern. Hands-on experience. Flexible working hours. Apply via email.",
        "Founding team at our startup seeks {skill} intern. Stipend {stipend}. Remote position.",
        "Student-friendly internship in {skill}. Our startup offers mentorship and stipend.",
        "{skill} intern needed at our early-stage startup. Work from home. No fee. Apply now.",
        "Hiring for {skill} role. Small but passionate team. Remote. Stipend {stipend} per month.",
    ],
    "upi_scam": [
        "Pay {amount} via UPI to confirm your {skill} internship at {company}. UPI ID: fastjobs@ybl. Urgent!",
        "Registration fee {amount} rupees for {skill} role at {company}. Send via GPay to 9988776655. Limited slots!",
        "UPI payment required to join {skill} internship at {company}. Send {amount} to register. WhatsApp HR.",
        "Pay registration fee via PhonePe for {skill} training. Amount {amount}. Internship at {company} starts immediately.",
        "Send {amount} via UPI to confirm your {skill} slot at {company}. UPI ID: quickjobs@paytm. Apply now!",
        "Internship fee {amount} via GPay for {skill} role at {company}. No interview. Immediate joining. WhatsApp now.",
        "UPI payment {amount} to activate your {skill} internship account at {company}. Send to bhim@upi.",
        "Registration via UPI only for {skill} role. Pay {amount} to start at {company}. Google Pay accepted. Urgent hiring.",
        "Pay {amount} via UPI to access {company} {skill} work portal. Earn 5000 daily. Limited openings.",
        "Confirm your {skill} slot at {company} by paying {amount} via PhonePe. Internship at top company.",
    ],
    "registration_fee_scam": [
        "Pay {amount} registration fee to start {skill} internship at {company}. No interview required. Join today!",
        "Registration fee {amount} rupees for {skill} work from home internship at {company}. WhatsApp HR now.",
        "Processing fee of {amount} required to confirm your {skill} internship at {company}. Apply immediately.",
        "Training fee {amount} rupees for {skill} program. Get {company} internship certificate. Earn from home. Join now!",
        "Pay {amount} application fee to secure your {skill} internship position at {company}. Limited seats available.",
        "One-time registration charge of {amount} rupees for {skill} role at {company}. Earn 3000 per day from home.",
        "Security deposit {amount} rupees for {skill} data entry internship at {company}. Refundable. Start today.",
        "Joining fee {amount} required for {skill} role. Online internship at {company}. No experience needed. WhatsApp HR.",
        "Platform access fee {amount} rupees for {skill} at {company}. Start earning from day one. No qualifications.",
        "Activation fee {amount} for {company} {skill} internship portal access. Work from mobile. Earn daily.",
    ],
    "captcha_scam": [
        "Captcha typing work from home. Earn {amount} per hour at {company}. Security deposit 1500 rupees. WhatsApp 9000011111.",
        "Captcha solving job at {company}. Earn {amount} daily. Registration fee {amount}. Work from mobile. Apply now.",
        "Simple captcha work for {company}. No skills needed. Earn {amount} per day. Pay {amount} to start. Immediate joining.",
        "Captcha entry job. Earn {amount} per hour from home. One-time fee of {amount} to join {company}. WhatsApp HR.",
        "Online captcha work at {company}. Flexible hours. Earn {amount} daily. Processing fee {amount} rupees. Join today!",
        "Captcha typing job available at {company}. Earn {amount} per 1000 captchas. Registration {amount} rupees. Start now.",
        "Home based captcha work for {company}. Earn {amount} daily guaranteed. Security deposit {amount} required. Apply now.",
        "Captcha solving from mobile. Earn {amount} per day at {company}. Training charge {amount} rupees. No experience.",
        "Simple captcha typing for {company}. Work 2 hours daily. Earn {amount}. Joining fee {amount} rupees. WhatsApp now.",
        "Captcha data entry work at {company}. Earn {amount} per hour. Platform fee {amount}. Unlimited earning potential.",
    ],
    "fake_internship": [
        "Earn {amount} weekly from home. No experience needed for {skill} role. Pay {amount} training fee. WhatsApp HR now.",
        "Work from home data entry for {company}. Earn {amount} per day. No qualification required. Registration fee {amount} applies.",
        "Online {skill} job opportunity at {company}. Earn {amount} daily. No skills needed. Small investment to start. Apply now.",
        "Part time {skill} work from home. Earn {amount} daily. Pay {amount} joining fee. WhatsApp now. Limited openings.",
        "Exciting opportunity: earn lakhs monthly from home with {company}. Minimal effort. Send {amount} to register for {skill} role.",
        "Remote {skill} job guaranteed at {company}. Earn {amount} weekly. No interview. Pay advance fee of {amount}. Immediate joining.",
        "MLM opportunity with {company}. Earn unlimited through referrals. Registration fee of {amount}. Build your network.",
        "Form filling job for {company}. Earn {amount} per form. No qualification. Pay {amount} advance. Start immediately.",
        "Copy paste work from home for {company}. Earn {amount} per task. Training fee of {amount} for {skill} training. Work 2 hours daily.",
        "Guaranteed income from home doing {skill} tasks. No experience required. Activation fee of {amount} applies. Join now."
    ]
}

# ============================================================
#  UNSEEN SCAM TEMPLATES (NEVER used in training/normal test)
# ============================================================

UNSEEN_SCAM_TEMPLATES = [
    "YouTube video liking work on {platform}. Earn {amount} per like. Transfer activation fee of {amount} to begin.",
    "Telegram review writing job for {company}. Review local businesses. Earn {amount} daily. Pay verification deposit of {amount}.",
    "Crypto trading internship at {company}. Earn commission by completing tasks. Transfer {amount} to open account.",
    "Application reviewer position. Review mobile apps on {platform} for {company}. Earn {amount} per app. Setup fee required.",
    "Refund agent internship. Process online orders. Refundable commitment fee of {amount} needed.",
    "Movie review typing job. Earn {amount} weekly. Security clearance charge of {amount} rupees applies.",
    "Google Map guide internship. Rate hotels on {platform} for {company}. Earn {amount} per day. Pay small training fee of {amount}.",
    "Product tester work. Test cosmetic items for {company}. Earn {amount} monthly. One-time processing fee of {amount} required.",
    "Social media manager assistant on {platform}. Earn {amount} daily. Access code activation charge of {amount} applies.",
    "SMS sending job on {platform}. Send promotional messages. Earn {amount} per SMS. Buy platform subscription for {amount}."
]

# ============================================================
#  SPLIT TEMPLATES INTO TRAIN AND TEST
#  80% Train, 20% Test/Benchmark
# ============================================================

TRAIN_TEMPLATES = {}
TEST_TEMPLATES = {}

for category, tmpl_list in TEMPLATES.items():
    split_idx = int(len(tmpl_list) * 0.8)
    # Ensure at least 1 template in test
    split_idx = max(1, min(split_idx, len(tmpl_list) - 1))
    
    TRAIN_TEMPLATES[category] = tmpl_list[:split_idx]
    TEST_TEMPLATES[category] = tmpl_list[split_idx:]

# ============================================================
#  GENERATOR IMPLEMENTATIONS WITH DUPLICATE FILTERING
# ============================================================

def generate_sample(category, template_pool):
    tmpl = random.choice(template_pool)
    skill = random.choice(SKILLS)
    company = random.choice(COMPANIES)
    stipend = random.choice(STIPENDS)
    amount = random.choice(["299", "499", "599", "799", "999", "1200", "1500"])
    platform = random.choice(["YouTube", "TikTok", "Instagram", "Facebook", "Telegram", "WhatsApp", "Google Maps", "Netflix", "Amazon Prime"])
    
    # Fill placeholders
    text = tmpl
    if "{skill}" in text:
        text = text.replace("{skill}", skill)
    if "{company}" in text:
        text = text.replace("{company}", company)
    if "{stipend}" in text:
        text = text.replace("{stipend}", stipend)
    if "{amount}" in text:
        if text.count("{amount}") > 1:
            amount2 = random.choice(["199", "350", "600", "850", "1100"])
            text = text.replace("{amount}", amount, 1)
            text = text.replace("{amount}", amount2)
        else:
            text = text.replace("{amount}", amount)
    if "{platform}" in text:
        text = text.replace("{platform}", platform)
        
    return text

def build_dataset(config, templates_map):
    """
    config: list of dicts with:
       - category: str (key in templates_map)
       - count: int
       - label: int
       - is_scam_slice: bool
    """
    samples = []
    generated_texts_set = set()
    generated_word_sets = []

    for item in config:
        category = item["category"]
        target_count = item["count"]
        label = item["label"]
        pool = templates_map[category]
        
        category_samples = 0
        attempts = 0
        
        while category_samples < target_count and attempts < target_count * 20:
            attempts += 1
            text = generate_sample(category, pool)
            
            # 1. Reject weak negatives
            if text.strip().lower() in ["hello", "good morning", "thank you", "hello!", "hi"]:
                continue
                
            # 2. Check exact duplicate
            if text in generated_texts_set:
                continue
                
            # 3. Check near-duplicate (similarity > 0.95)
            w1 = set(text.lower().split())
            is_dup = False
            for w2 in generated_word_sets:
                union_len = len(w1 | w2)
                if union_len > 0 and len(w1 & w2) / union_len > 0.95:
                    is_dup = True
                    break
                    
            if is_dup:
                continue
                
            # Valid sample
            generated_texts_set.add(text)
            generated_word_sets.append(w1)
            
            # Assign URL
            if label == 1:
                # Scam domains
                tlds = [".xyz", ".tk", ".top", ".online", ".ru"]
                url = f"http://{''.join(random.choices('abcdefghijklmnop', k=8))}{random.choice(tlds)}"
            else:
                url = random.choice(LEGIT_URLS)
                
            samples.append({
                "text": text,
                "label": label,
                "url": url,
                "scam_type": category,
                "payment_flag": 1 if "scam" in category or category == "fake_internship" else 0,
                "urgency_score": random.randint(5, 10) if label == 1 else random.randint(0, 3),
                "work_mode": "remote",
                "company_name": random.choice(["QuickJobs", "FastEarn", "EasyTask"]) if label == 1 else random.choice(COMPANIES)
            })
            category_samples += 1
            
        print(f"  Generated {category_samples} samples for {category} (attempts: {attempts})")
        
    return samples

# ============================================================
#  ADVERSARIAL OBFUSCATION GENERATOR
# ============================================================

def make_adversarial(text):
    # Programmatically apply obfuscation patterns
    words = text.split()
    new_words = []
    for w in words:
        w_lower = w.lower()
        if "fee" in w_lower:
            w = w.replace("fee", "f€e").replace("FEE", "F€E")
        elif "payment" in w_lower:
            w = w.replace("payment", "pa¥ment").replace("PAYMENT", "PA¥MENT")
        elif "free" in w_lower:
            w = w.replace("free", "fr33").replace("FREE", "FR33")
        elif "not" in w_lower:
            w = "n.o.t"
        elif "upi" in w_lower:
            w = "u_p_i"
        new_words.append(w)
    return " ".join(new_words)

def generate_adversarial_slice(count=50):
    scam_categories = ["upi_scam", "registration_fee_scam", "captcha_scam", "fake_internship"]
    samples = []
    generated_texts = []
    
    while len(samples) < count:
        cat = random.choice(scam_categories)
        # Use test templates to generate base scam
        text = generate_sample(cat, TEST_TEMPLATES[cat])
        adv_text = make_adversarial(text)
        
        # Check duplicate
        if adv_text in generated_texts:
            continue
            
        generated_texts.append(adv_text)
        tlds = [".xyz", ".tk", ".top", ".online"]
        url = f"http://{''.join(random.choices('abcdefghijklmnop', k=8))}{random.choice(tlds)}"
        
        samples.append({
            "text": adv_text,
            "label": 1,
            "url": url,
            "scam_type": "adversarial_obfuscation",
            "payment_flag": 1,
            "urgency_score": random.randint(6, 10),
            "work_mode": "remote",
            "company_name": "Adversarial Lab"
        })
    return samples

# ============================================================
#  MAIN EXECUTION
# ============================================================

FIELDNAMES = [
    "text", "label", "url", "scam_type",
    "payment_flag", "urgency_score", "work_mode", "company_name"
]

def write_csv(filename, samples):
    filepath = os.path.join("dataset", filename)
    os.makedirs("dataset", exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        random.shuffle(samples)
        for sample in samples:
            writer.writerow(sample)
    print(f"Written {len(samples)} samples to {filepath}\n")

if __name__ == "__main__":
    print("============================================================")
    print(" GENERATING Balanced Training Dataset (expanded_dataset.csv)")
    print("============================================================")
    
    # 1500 samples balanced according to production distribution:
    # 40% legit recruiting (LinkedIn 30% + Course Promo 10%)
    # 20% recruiter updates
    # 15% startup hiring
    # 10% onboarding (WhatsApp 4% + Telegram legit 3% + Campus 3%)
    # 15% scams (UPI 5% + Registration 5% + Captcha/Fake 5%)
    train_config = [
        {"category": "linkedin_networking", "count": 450, "label": 0},
        {"category": "course_promotion", "count": 150, "label": 0},
        {"category": "recruiter_update", "count": 300, "label": 0},
        {"category": "startup_hiring", "count": 225, "label": 0},
        {"category": "whatsapp_onboarding", "count": 60, "label": 0},
        {"category": "telegram_legit", "count": 45, "label": 0},
        {"category": "campus_ambassador", "count": 45, "label": 0},
        {"category": "upi_scam", "count": 75, "label": 1},
        {"category": "registration_fee_scam", "count": 75, "label": 1},
        {"category": "captcha_scam", "count": 75, "label": 1},
    ]
    train_samples = build_dataset(train_config, TRAIN_TEMPLATES)
    write_csv("expanded_dataset.csv", train_samples)
    
    print("============================================================")
    print(" GENERATING Benchmark Dataset (benchmark_dataset.csv)")
    print("============================================================")
    
    # 600 samples, 12 slices of 50 samples each:
    # All generated from TEST templates (disjoint from train)
    benchmark_config = [
        {"category": "linkedin_networking", "count": 50, "label": 0},
        {"category": "recruiter_update", "count": 50, "label": 0},
        {"category": "campus_ambassador", "count": 50, "label": 0},
        {"category": "whatsapp_onboarding", "count": 50, "label": 0},
        {"category": "telegram_legit", "count": 50, "label": 0},
        {"category": "course_promotion", "count": 50, "label": 0},
        {"category": "startup_hiring", "count": 50, "label": 0},
        {"category": "upi_scam", "count": 50, "label": 1},
        {"category": "registration_fee_scam", "count": 50, "label": 1},
        {"category": "captcha_scam", "count": 50, "label": 1},
    ]
    
    benchmark_samples = build_dataset(benchmark_config, TEST_TEMPLATES)
    
    # Add Adversarial slice (50)
    print("  Generating adversarial obfuscation slice...")
    adv_samples = generate_adversarial_slice(50)
    benchmark_samples.extend(adv_samples)
    
    # Add Unseen Scam slice (50)
    print("  Generating unseen scam slice for benchmark...")
    unseen_bench_texts = []
    unseen_bench_samples = []
    attempts = 0
    while len(unseen_bench_samples) < 50 and attempts < 1000:
        attempts += 1
        text = generate_sample("unseen", UNSEEN_SCAM_TEMPLATES)
        if text not in unseen_bench_texts:
            unseen_bench_texts.append(text)
            url = f"http://{''.join(random.choices('abcdefghijklmnop', k=8))}.online"
            unseen_bench_samples.append({
                "text": text,
                "label": 1,
                "url": url,
                "scam_type": "unseen_scam",
                "payment_flag": 1,
                "urgency_score": random.randint(7, 10),
                "work_mode": "remote",
                "company_name": "Unseen Group"
            })
    benchmark_samples.extend(unseen_bench_samples)
    write_csv("benchmark_dataset.csv", benchmark_samples)

    print("============================================================")
    print(" GENERATING Unseen Scam Test Dataset (unseen_scam_test.csv)")
    print("============================================================")
    
    # 500 samples of unseen scams
    unseen_test_texts = []
    unseen_test_samples = []
    attempts = 0
    while len(unseen_test_samples) < 500 and attempts < 10000:
        attempts += 1
        text = generate_sample("unseen", UNSEEN_SCAM_TEMPLATES)
        # Prevent duplicate with benchmark unseen scam samples
        if text not in unseen_bench_texts and text not in unseen_test_texts:
            unseen_test_texts.append(text)
            url = f"http://{''.join(random.choices('abcdefghijklmnop', k=8))}.net"
            unseen_test_samples.append({
                "text": text,
                "label": 1,
                "url": url,
                "scam_type": "unseen_scam",
                "payment_flag": 1,
                "urgency_score": random.randint(7, 10),
                "work_mode": "remote",
                "company_name": "Unseen Corp"
            })
    write_csv("unseen_scam_test.csv", unseen_test_samples)
    
    print("Dataset generation complete!")
