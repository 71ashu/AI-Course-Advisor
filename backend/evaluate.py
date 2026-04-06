"""Evaluation script for recommendation quality using leave-one-out protocol.

For each synthetic student, holds out each completed course one at a time,
runs the recommender, and checks whether the held-out course appears in top-k.

Usage:
    python evaluate.py
"""
from app import app
from models import db, Student, StudentCourse
from services import get_recommendations


def evaluate(k_values=None):
    if k_values is None:
        k_values = [3, 6]

    with app.app_context():
        students = Student.query.filter_by(is_synthetic=True).all()
        if not students:
            print("No synthetic students found. Run seed.py first.")
            return

        print(f"Evaluating on {len(students)} synthetic students...")
        print(f"k values: {k_values}\n")

        results = {k: {'hits': 0, 'precision_sum': 0.0, 'recall_sum': 0.0, 'total': 0}
                   for k in k_values}

        for student in students:
            completed = StudentCourse.query.filter_by(
                student_id=student.id, status='completed'
            ).all()

            if len(completed) < 2:
                continue

            for holdout_enrollment in completed:
                held_out_id = holdout_enrollment.course_id

                # Temporarily remove the held-out course
                original_status = holdout_enrollment.status
                holdout_enrollment.status = '_holdout'
                db.session.flush()

                try:
                    recs = get_recommendations(student, query='')
                    rec_ids = [r['course_number'] for r in recs]

                    for k in k_values:
                        top_k = rec_ids[:k]
                        hit = 1 if held_out_id in top_k else 0
                        results[k]['hits'] += hit
                        results[k]['precision_sum'] += hit / k
                        results[k]['recall_sum'] += hit  # recall@k with 1 relevant item
                        results[k]['total'] += 1

                finally:
                    holdout_enrollment.status = original_status
                    db.session.flush()

        print("=" * 60)
        print(f"{'Metric':<25} {'Value':>10}")
        print("=" * 60)

        for k in k_values:
            r = results[k]
            total = r['total']
            if total == 0:
                print(f"  k={k}: No evaluations possible")
                continue

            hit_rate = r['hits'] / total
            precision = r['precision_sum'] / total
            recall = r['recall_sum'] / total

            print(f"  Hit Rate@{k:<14} {hit_rate:>10.4f}")
            print(f"  Precision@{k:<13} {precision:>10.4f}")
            print(f"  Recall@{k:<16} {recall:>10.4f}")
            print(f"  Total evaluations:     {total:>10}")
            print("-" * 60)

        print("\nDone.")
        return results


if __name__ == '__main__':
    evaluate()
